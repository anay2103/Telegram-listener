import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from telethon import TelegramClient

import bot.settings as settings

logger = logging.getLogger(__name__)


class PostgresMixin:

    def __init__(self) -> None:
        self.engine = None
        self.db_session = None

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

    def __init__(self, bot: Optional['Client'] = None, **kwargs) -> None:
        """Клиент может иметь атрибутом бот для пересылки сообщений пользователям."""
        self.bot = bot
        super().__init__(**kwargs)
