import logging

import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from telethon import TelegramClient

logger = logging.getLogger(__name__)


class PostgresMixin:

    def __init__(self, **kwargs) -> None:
        self.engine = None
        self.db_session = None
        super().__init__()

    def db_connect(self) -> None:
        try:
            engine = create_async_engine(settings.POSTGRES_URI, echo=True)
        except Exception as error:
            logger.error(error, exc_info=True)
            raise
        self.engine = engine

        try:
            session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        except Exception as error:
            logger.error(error, exc_info=True)
            raise
        self.db_session = session


class Client(TelegramClient, PostgresMixin):
    """Клиент Телеграма с доступом в БД."""
