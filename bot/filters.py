"""Фильтры для сообщений Телеграма."""

from typing import TYPE_CHECKING, Optional

from telethon.events import common as events
from telethon.tl import types

from bot.schemas import Grades, Languages

if TYPE_CHECKING:
    import bot.models as models


async def is_superuser(event: events.EventCommon) -> bool:
    """Фильтр по суперюзеру."""
    user = await event.client.get_user(user_id=event.sender.id)
    return bool(user and user.is_superuser)


async def filter_status(event: events.EventCommon, status: str) -> bool:
    """Фильтр пользователей по статусу."""
    state = await event.client.get_state(event.sender.id)
    return state == status


async def selected_chat(event: events.EventCommon) -> Optional['models.Channel']:
    """Фильтр чатов, которые сохранены в БД."""
    if isinstance(event.peer_id, types.PeerUser):
        chat_id = event.peer_id.user_id
    elif isinstance(event.peer_id, types.PeerChat):
        chat_id = event.peer_id.chat_id
    else:
        chat_id = event.peer_id.channel_id

    return await event.client.get_chat(chat_id=abs(chat_id))


async def choosing_language(event: events.EventCommon) -> bool:
    """Фильтр входящего сообщения по названию ЯП."""
    language = event.data.decode()
    return language in Languages._member_names_


async def choosing_grade(event: events.EventCommon) -> bool:
    """Фильтр входящего сообщения по названию грейда."""
    grade = event.data.decode()
    return grade in Grades._member_names_
