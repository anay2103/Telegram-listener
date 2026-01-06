from collections import defaultdict

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

from bot import settings
from bot.chromadb import ChromaService
from bot.chromadb.client import get_chromadb_collection
from bot.chromadb.schemas import GetResultProxy, convert_from_get_result, convert_to_get_result

from .prompts import CHOOSE_VACANCY_PROMPT
from .schemas import HHAgentOutput


class Agent:
    def __init__(self, documents: list, bot):
        self.bot = bot
        self.documents = documents
        self.doc_ids = [d.doc_id for d in self.documents]
        self.vacancies_service = self.get_chromadb_service(settings.CHROMA_VACANCIES_COLLECTION)
        self.queries_service = self.get_chromadb_service(settings.CHROMA_QUERIES_COLLECTION)
        self.index = self.get_index()
        self.docstore = self.index.storage_context.docstore
        self.agent = FunctionAgent(
            tools=[self.retrieve_documents],
            llm=OpenAI(model='gpt-4o-mini'),
            system_prompt=CHOOSE_VACANCY_PROMPT,
            output_cls=HHAgentOutput,
        )

    def get_index(self):
        storage = StorageContext.from_defaults()
        storage.docstore.add_documents(self.documents)
        index = VectorStoreIndex.from_documents(self.documents, storage_context=storage)
        return index

    def get_chromadb_service(self, collection_name: str) -> ChromaService:
        collection = get_chromadb_collection(name=collection_name)
        return ChromaService(collection)

    def retrieve_documents(self, query: str, sended_docs: list[int], nodes_k: int = 30, top_k_docs: int = 10):
        retriever = self.index.as_retriever(similarity_top_k=nodes_k)
        nodes = retriever.retrieve(query)
        by_doc = defaultdict(list)
        for n in nodes:
            by_doc[n.node.ref_doc_id].append(n.score)
        scored_doc_ids = sorted(
            [(doc_id, sum(scores)) for doc_id, scores in by_doc.items() if doc_id not in sended_docs],
            key=lambda x: x[1],
            reverse=True,
        )[:top_k_docs]
        return [(self.docstore.get_document(doc_id), score) for doc_id, score in scored_doc_ids]

    def save_documents(self):
        self.vacancies_service.upsert(
            ids=self.doc_ids,
            documents=[d.text for d in self.documents],
            metadatas=[d.metadata for d in self.documents],
        )

    def update_queries(self, queries: GetResultProxy):
        self.queries_service.upsert(
            ids=queries['ids'],
            documents=queries['documents'],
            metadatas=queries['metadatas'],
        )

    async def run(self):
        getresult = self.queries_service.get(include=['documents', 'metadatas'])
        queries = convert_from_get_result(getresult)
        for query in queries:
            user_id = query['metadatas']['user_id']
            sended_ids = query['metadatas'].get('vacancies', [])
            result = await self.agent.run(query['document'], sended_ids)
            vacancies, ids = result.structured_response.get('vacancies', []), result.structured_response.get('ids', [])
            if vacancies:
                await self.bot.send_message(user_id, str(vacancies))
            query['metadatas']['vacancies'] = [*sended_ids, *ids]

        self.update_queries(convert_to_get_result(queries))
        if self.documents:
            self.save_documents()
