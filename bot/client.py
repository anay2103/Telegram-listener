"""Клиент Телеграма."""
import json
import logging
from typing import Any, Coroutine, Optional

from aiolimiter import AsyncLimiter
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from redis import asyncio as aioredis
from telethon import TelegramClient, hints
from telethon.tl import types

from bot import settings
from bot.service import TelegramService
from bot.openai import OpenAIClient


class Client(OpenAIClient, TelegramService, TelegramClient):
    """Клиент Телеграма с доступом в БД и кэш Redis."""

    def __init__(
        self,
        bot: Optional['Client'] = None,
        **kwargs,
    ) -> None:
        """Клиент может иметь атрибутом бот для пересылки сообщений пользователям."""
        self.bot = bot
        self.redis: Optional[aioredis.Redis] = None
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

    def redis_connect(self) -> None:
        """Подключение к Redis."""
        uri = settings.build_redis_uri()
        try:
            redis = aioredis.from_url(uri, encoding='utf-8', decode_responses=True)
        except Exception as error:
            logging.error(error, exc_info=True)
            raise
        self.redis = redis

    async def set_state(self, key: str, data: Optional[Any] = None) -> None:
        """Добавление пары ключ-значение в Redis."""
        if not self.redis:
            self.redis_connect()
        try:
            await self.redis.set(key, json.dumps(data))  # type: ignore
        except Exception as error:
            logging.error(error, exc_info=True)
            return

    async def get_state(self, key: str) -> Any:
        """Получение значения по ключу в Redis."""
        if not self.redis:
            self.redis_connect()
        value = (await self.redis.get(key))  # type: ignore
        if value:
            return json.loads(value)

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
