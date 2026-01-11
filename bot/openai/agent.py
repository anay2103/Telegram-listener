import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader
from llama_index.core import PromptTemplate, StorageContext, VectorStoreIndex, get_response_synthesizer
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from sqlalchemy.exc import IntegrityError

from bot import models, settings
from bot.chromadb.client import get_chromadb_collection
from bot.chromadb.schemas import convert_from_get_result

from ..chromadb.service import get_chromadb_service
from .prompts import CHOOSE_VACANCY_PROMPT
from .schemas import HHAgentOutput

if TYPE_CHECKING:
    from bot.client import Client

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, documents: list, bot: 'Client'):
        self.bot = bot
        self.documents = documents
        self.doc_ids = [d.doc_id for d in self.documents]
        self.chroma_vacancies_service = get_chromadb_service(settings.CHROMA_VACANCIES_COLLECTION)
        self.queries_service = get_chromadb_service(settings.CHROMA_QUERIES_COLLECTION)
        self.index = self.get_index()
        self.reranker = LLMRerank(top_n=5)
        self.template = Environment(loader=FileSystemLoader('bot/templates')).get_template('tg_msg_vacancy.txt')
        self.response_synthesizer = get_response_synthesizer(
            response_mode='compact',
            llm=OpenAI(model='gpt-5-nano'),
            text_qa_template=PromptTemplate(CHOOSE_VACANCY_PROMPT),
            output_cls=HHAgentOutput,
        )

    def get_index(self):
        collection = get_chromadb_collection(settings.CHROMA_VACANCIES_COLLECTION)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store, storage_context=storage, embed_model=OpenAIEmbedding(model=settings.CHROMA_EMBEDDING_MODEL)
        )
        return index

    async def retrieve_documents(self, query: str, user_id: int, nodes_k: int = 20):
        seen_docs = await self.bot.vacancy_service.get_list(models.Vacancy.user_id == user_id)
        seen_ids = [str(item.id) for item in seen_docs]
        date_filter = int((datetime.now() - timedelta(days=2)).timestamp())
        filters = [
            MetadataFilter(key='published_at_ts', operator=FilterOperator.GTE, value=date_filter),
        ]
        if seen_ids:
            filters.append(
                MetadataFilter(
                    key='id',
                    operator=FilterOperator.NIN,
                    value=seen_ids,
                )
            )
        retriever = self.index.as_retriever(
            similarity_top_k=nodes_k, similarity_cutoff=0.7, filters=MetadataFilters(filters=filters)
        )
        nodes = retriever.retrieve(query)
        reranked_nodes = self.reranker.postprocess_nodes(nodes, query_str=query)
        logger.info(f'Nodes returned by reranker {nodes}')
        return self.response_synthesizer.synthesize(query=query, nodes=reranked_nodes)

    def save_documents(self) -> None:
        if self.documents:
            self.chroma_vacancies_service.upsert(
                ids=self.doc_ids,
                documents=[d.text for d in self.documents],
                metadatas=[d.metadata for d in self.documents],
            )

    async def update_vacancies(self, ids: list[str], user_id: int) -> None:
        for id_ in ids:
            try:
                await self.bot.vacancy_service.add_item(id=int(id_), user_id=user_id, source='hh.ru')
            except IntegrityError:
                pass

    async def run(self):
        getresult = self.queries_service.get(include=['documents', 'metadatas'])
        queries = convert_from_get_result(getresult)
        for query in queries:
            user_id = query['metadatas']['user_id']
            result = await self.retrieve_documents(query['document'], user_id=user_id)
            if not hasattr(result.response, 'vacancies'):
                logger.info('Empty response, continuing...')
                continue
            logger.info(f'Response source nodes {result.source_nodes}')
            vacancies = result.response.model_dump()['vacancies']
            text = self.template.render(vacancies=vacancies)
            await self.bot.send_message(user_id, text)
            logging.info(f'Sended HH vacancies to {user_id}')
            await self.update_vacancies(ids=[v['id'] for v in vacancies], user_id=user_id)
