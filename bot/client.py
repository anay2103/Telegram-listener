"""Клиент Телеграма."""
import json
import logging
from typing import Any, Coroutine, Dict, List, Optional

import aioredis
from aiolimiter import AsyncLimiter
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker
from telethon import TelegramClient, hints
from telethon.tl import types

from bot import settings

logger = logging.getLogger(__name__)


class Client(TelegramClient):
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
        self.db_session: Optional[sessionmaker[AsyncSession]] = None
        self.limiter = AsyncLimiter(settings.MESSAGE_RATE_LIMIT)
        super().__init__(**kwargs)

    def db_connect(self) -> None:
        """Подключение к БД."""
        uri = settings.build_postgres_uri()
        try:
            engine = create_async_engine(uri, echo=True)
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

    def redis_connect(self) -> None:
        """Подключение к Redis."""
        uri = settings.build_redis_uri()
        try:
            redis = aioredis.from_url(uri, encoding='utf-8', decode_responses=True)
        except Exception as error:
            logger.error(error, exc_info=True)
            raise
        self.redis = redis

    async def set_state(self, key: str, value: Any) -> None:
        """Добавление пары ключ-значение в Redis."""
        if not self.redis:
            self.redis_connect()
        if isinstance(value, List):
            value = dict.fromkeys(value)
        await self.redis.set(key, json.dumps(value))  # type: ignore

    async def get_state(self, key: str) -> Dict[str, Any]:
        """Получение значения по ключу в Redis."""
        if not self.redis:
            self.redis_connect()
        value = await self.redis.get(key)  # type: ignore
        return json.loads(value)

    async def send_message(
        self,
        entity: hints.EntityLike,
        message: types.Message,
        **kwargs: Any,
    ) -> Coroutine[Any, Any, types.Message]:
        """Отправка сообщений с учетом ограничений Телеграма."""
        async with self.limiter:
            return await super().send_message(entity, message, **kwargs)
