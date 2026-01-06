import logging

from aiolimiter import AsyncLimiter
from celery import shared_task

from bot import settings
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
        logger.info('Fetching vacancies from hh.ru')
        page, total_pages, total_items = 0, 1, 0
        while page <= total_pages:
            vacancies_response = await hh_service.get_vacancies(page=page)
            total_pages = vacancies_response.pages
            total_items = vacancies_response.found
            page += 1
            logger.info(f'Found {total_items} total vacancies across {total_pages} pages')

            documents = []

            for vacancy in vacancies_response.items:
                async with limiter:
                    try:
                        document = await hh_service.get_vacancy_detail(vacancy.id)
                        documents.append(document)
                        logger.debug(f'Processed vacancy {vacancy.id}')
                    except Exception as e:
                        logger.error(f'Error processing vacancy {vacancy.id}: {e}', exc_info=True)
                        continue

            logger.info('building index from texts...')
            async with bot:
                agent = Agent(documents=documents, bot=bot)
                await agent.run()
            logger.info(f'Successfully saved {len(agent.documents)} documents to ChromaDB')

        logger.info(f'Collected {total_items} vacancies from all pages')
