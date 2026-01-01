"""Клиент Телеграма."""

import logging
from typing import Any, Coroutine, Optional

from aiolimiter import AsyncLimiter
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from telethon import TelegramClient, hints
from telethon.tl import types

from bot import settings
from bot.openai import OpenAIClient
from bot.service import ChannelService, CVService, SearchItemsService, UserService


class Client(OpenAIClient, TelegramClient):
    """Клиент Телеграма с доступом в БД и кэш Redis."""

    def __init__(
        self,
        bot: Optional['Client'] = None,
        **kwargs,
    ) -> None:
        """Клиент может иметь атрибутом бот для пересылки сообщений пользователям."""
        self.bot = bot
        self.engine: Optional[AsyncEngine] = None
        self.sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None
        self.limiter = AsyncLimiter(settings.MESSAGE_RATE_LIMIT)
        self.flood_sleep_threshold = settings.FLOOD_WAIT_THRESHOLD
        self.db_connect()
        self.user_service = UserService(self.sessionmaker)
        self.channel_service = ChannelService(self.sessionmaker)
        self.searchitems_service = SearchItemsService(self.sessionmaker)
        self.cv_service = CVService(self.sessionmaker)
        super().__init__(**kwargs)

    def db_connect(self) -> None:
        """Подключение к БД."""
        uri = settings.build_postgres_uri()
        try:
            engine = create_async_engine(uri)
        except Exception as error:
            logging.error(error, exc_info=True)
            raise
        self.engine = engine
        self.sessionmaker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def process_message(self, message: str) -> set[int]:
        """Обработка входящего сообщения:

        запрос параметров сообщения у ИИ и поиск пользователей с заданными параметрами.
        """
        summary = await self.ai_request(message)
        match = await self.searchitems_service.get_searchitems(languages=summary.languages_lower, grades=summary.grades)
        return set(match)

    async def send_message(
        self,
        entity: hints.EntityLike,
        message: types.Message,
        **kwargs: Any,
    ) -> Coroutine[Any, Any, types.Message]:
        """Отправка сообщений с учетом ограничений Телеграма."""
        async with self.limiter:
            return await super().send_message(entity, message, **kwargs)
