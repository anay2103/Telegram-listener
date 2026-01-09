import logging
from datetime import datetime, timedelta

from aiolimiter import AsyncLimiter
from celery import shared_task
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot import models, settings
from bot.chromadb.service import get_chromadb_service
from bot.client import get_tg_bot
from bot.hh.client import HHClient
from bot.hh.service import HHService
from bot.openai.agent import Agent

from .base import AsyncTask

logger = logging.getLogger(__name__)


@shared_task(base=AsyncTask)
async def poll_hh():
    """Опрос API hh.ru и сохранение вакансий в ChromaDB."""
    async with HHClient() as hh_client:
        hh_service = HHService(hh_client)
        bot = get_tg_bot()
        bot.start(bot_token=settings.BOT_TOKEN)
        logging.info('Bot successfully started')
        limiter = AsyncLimiter(1, 1)
        chroma_vacancies_service = get_chromadb_service(settings.CHROMA_VACANCIES_COLLECTION)
        logger.info('Fetching vacancies from hh.ru')
        page, total_pages, total_items = 0, 1, 0
        doc_ids = set()
        documents = []
        while page <= total_pages:
            vacancies_response = await hh_service.get_vacancies(page=page)
            total_pages = vacancies_response.pages
            total_items = vacancies_response.found
            page += 1
            logger.info(f'Found {total_items} total vacancies across {total_pages} pages')

            for vacancy in vacancies_response.items:
                async with limiter:
                    try:
                        document = await hh_service.get_vacancy_detail(vacancy.id)
                        if document.doc_id not in doc_ids:
                            documents.append(document)
                            doc_ids.add(document.doc_id)
                        logger.debug(f'Processed vacancy {vacancy.id}')
                    except Exception as e:
                        logger.error(f'Error processing vacancy {vacancy.id}: {e}', exc_info=True)
                        continue
        already_saved = chroma_vacancies_service.get(ids=[*doc_ids], include=[])
        saved_ids = set(already_saved['ids'])
        new_docs = list(filter(lambda x: x.doc_id not in saved_ids, documents))
        logger.info(f'Found {len(new_docs)} new vacancies')
        async with bot:
            agent = Agent(documents=new_docs, bot=bot)
            agent.save_documents()
            await agent.run()


@shared_task(base=AsyncTask)
async def delete_old_vacancies():
    """Удаление вакансий, созданных больше недели назад."""
    uri = settings.build_postgres_uri()
    engine = create_async_engine(uri)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    try:
        # Вычисляем дату неделю назад
        week_ago = datetime.now() - timedelta(days=7)

        async with sessionmaker.begin() as session:
            # Удаляем вакансии старше недели
            query = delete(models.Vacancy).where(models.Vacancy.created_at < week_ago)
            result = await session.execute(query)
            deleted_count = result.rowcount

        logger.info(f'Deleted {deleted_count} vacancies older than 7 days')
    except Exception as e:
        logger.error(f'Error deleting old vacancies: {e}', exc_info=True)
        raise
    finally:
        await engine.dispose()
