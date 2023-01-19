"""Фильтры для сообщений Телеграма."""
from typing import TYPE_CHECKING

from telethon.events import common as events

from bot.repository import ChannelRepository, UserRepository

if TYPE_CHECKING:
    import bot.models as models


async def is_superuser(event: events.EventCommon) -> bool:
    """Фильтр по суперюзеру."""
    session = event.client.db_session()
    user = await UserRepository(session=session).get(id=event.sender.id)
    await session.commit()
    return user.is_superuser


async def selected_chat(event: events.EventCommon) -> 'models.Channel':
    """
    Фильтр чата, который есть в БД.
    Сообщения из этих чатов преверяются на наличие ключевых слов
    """
    chat_id = abs(event.chat_id)  # id чатов ТГ отрицательные, в БД положительные
    session = event.client.db_session()
    chat = await ChannelRepository(session=session).get(id=chat_id)
    await session.commit()
    return chat
