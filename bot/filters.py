"""Фильтры для сообщений Телеграма."""
from typing import TYPE_CHECKING

from telethon.events import common as events
from telethon.tl import types

from bot.crud import ChannelRepository

if TYPE_CHECKING:
    import bot.models as models


async def is_superuser(event: events.EventCommon) -> bool:
    """Фильтр по суперюзеру."""
    user = await event.client.user_repository.get(id=event.sender.id)
    return bool(user.is_superuser)


async def filter_status(event: events.EventCommon, status: str) -> bool:
    """Фильтр пользователей по статусу."""
    state = await event.client.get_state(event.sender.id)
    return state == status


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
