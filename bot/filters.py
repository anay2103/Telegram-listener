"""Фильтры для сообщений Телеграма."""
from enum import Enum
from typing import TYPE_CHECKING

from telethon.events import common as events
from telethon.tl import types

from bot.crud import ChannelRepository

if TYPE_CHECKING:
    import bot.models as models


class ChoosingGradeState(str, Enum):
    """Статусы пользователя."""

    сhoosing_grade = 'choosing grade'
    choosing_no_grade_ok = 'choosing no grade ok'


class ChannelAdminState(str, Enum):
    """Статусы админа при работе с чатами."""

    adding_channel = 'adding_channel'
    deleting_channel = 'deleting_channel'


async def is_superuser(event: events.EventCommon) -> bool:
    """Фильтр по суперюзеру."""
    user = await event.client.user_repository.get(id=event.sender.id)
    return bool(user.is_superuser)


async def choosing_grade(event: events.EventCommon) -> bool:
    """Фильтр пользователей, которые находятся в статусе выбора грейда."""
    state = await event.client.get_state(event.sender.id)
    return state == ChoosingGradeState.сhoosing_grade


async def сhoosing_no_grade_ok(event: events.EventCommon) -> bool:
    """Фильтр пользователей, которые находятся в статусе выбора

    подписки на вакансии без указания грейда."""
    state = await event.client.get_state(event.sender.id)
    return state == ChoosingGradeState.choosing_no_grade_ok and event.query is not None


async def adding_channel(event: events.EventCommon) -> bool:
    """Фильтр админа, который находится в статусе добавления чата."""
    state = await event.client.get_state(event.sender.id)
    return state == ChannelAdminState.adding_channel


async def deleting_channel(event: events.EventCommon) -> bool:
    """Фильтр админа, который находится в статусе удаления чата."""
    state = await event.client.get_state(event.sender.id)
    return state == ChannelAdminState.deleting_channel


async def selected_chat(event: events.EventCommon) -> 'models.Channel':
    """Фильтр чатов, которые сохранены в БД."""
    if isinstance(event.peer_id, types.PeerUser):
        chat_id = event.peer_id.user_id
    elif isinstance(event.peer_id, types.PeerChat):
        chat_id = event.peer_id.chat_id
    else:
        chat_id = event.peer_id.channel_id

    session = event.client.db_session
    return await ChannelRepository(session=session).get(id=abs(chat_id))
