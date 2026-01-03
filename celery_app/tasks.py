import logging

from aiolimiter import AsyncLimiter
from celery import shared_task

from bot.chromadb.client import get_chromadb_collection
from bot.chromadb.service import ChromaService
from bot.hh.client import HHClient
from bot.hh.service import HHService
from celery_app.base import AsyncTask

logger = logging.getLogger(__name__)


@shared_task(base=AsyncTask)
async def poll_hh():
    """Опрос API hh.ru и сохранение вакансий в ChromaDB."""
    async with HHClient() as hh_client:
        hh_service = HHService(hh_client)
        chroma_collection = get_chromadb_collection()
        chroma_service = ChromaService(chroma_collection)
        limiter = AsyncLimiter(2, 1)

        logger.info('Fetching vacancies from hh.ru')
        page, total_pages, total_items = 0, 1, 0
        while page <= total_pages:
            vacancies_response = await hh_service.get_vacancies(page=page)
            total_pages = vacancies_response.pages
            total_items = vacancies_response.found
            page += 1
            logger.info(f'Found {total_items} total vacancies across {total_pages} pages')

            ids = []
            texts = []
            metadatas = []

            for vacancy in vacancies_response.items:
                async with limiter:
                    try:
                        document = await hh_service.get_vacancy_detail(vacancy.id)
                        ids.append(document.id)
                        texts.append(document.text)
                        metadatas.append(document.metadata)
                        logger.debug(f'Processed vacancy {vacancy.id}')
                    except Exception as e:
                        logger.error(f'Error processing vacancy {vacancy.id}: {e}', exc_info=True)
                        continue

            # Сохраняем все документы в ChromaDB
            if ids:
                chroma_service.upsert(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                )
                logger.info(f'Successfully saved {len(ids)} documents to ChromaDB')
            else:
                logger.warning('No documents to save')

        logger.info(f'Collected {total_items} vacancies from all pages')
