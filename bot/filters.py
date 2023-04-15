"""Фильтры для сообщений Телеграма."""
from enum import Enum
from typing import TYPE_CHECKING

from telethon.events import common as events
from telethon.tl import types

from bot.crud import ChannelRepository, UserRepository

if TYPE_CHECKING:
    import bot.models as models


class State(str, Enum):
    """Статусы пользователя."""

    adding = 'adding keywords'
    deleting = 'deleting keywords'


async def is_superuser(event: events.EventCommon) -> bool:
    """Фильтр по суперюзеру."""
    session = event.client.db_session
    user = await UserRepository(session=session).get(id=event.sender.id)
    return bool(user.is_superuser)


async def is_adding(event: events.EventCommon) -> bool:
    """Фильтр пользователей, которые находятся в статусе добавления слов."""
    state = await event.client.get_state(event.sender.id)
    return state == State.adding


async def is_deleting(event: events.EventCommon) -> bool:
    """Фильтр пользователей, которые находятся в статусе удаления слов."""
    state = await event.client.get_state(event.sender.id)
    return state == State.deleting


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
