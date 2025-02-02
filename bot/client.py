"""Клиент Телеграма."""

import logging
from typing import Any, Coroutine, Optional

from aiolimiter import AsyncLimiter
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from telethon import TelegramClient, hints
from telethon.tl import types

from bot import settings
from bot.openai import OpenAIClient
from bot.service import TelegramService


class Client(OpenAIClient, TelegramService, TelegramClient):
    """Клиент Телеграма с доступом в БД и кэш Redis."""

    def __init__(
        self,
        bot: Optional['Client'] = None,
        **kwargs,
    ) -> None:
        """Клиент может иметь атрибутом бот для пересылки сообщений пользователям."""
        self.bot = bot
        self.engine: Optional[AsyncEngine] = None
        self.limiter = AsyncLimiter(settings.MESSAGE_RATE_LIMIT)
        self.flood_sleep_threshold = settings.FLOOD_WAIT_THRESHOLD
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

    async def process_message(self, message: str) -> set[int]:
        """Обработка входящего сообщения:

        запрос параметров сообщения у ИИ и поиск пользователей с заданными параметрами.
        """
        summary = await self.ai_request(message)
        match = await self.get_searchitems(languages=summary.language, grades=summary.grade)
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
