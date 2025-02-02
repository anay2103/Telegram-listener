"""Фильтры для сообщений Телеграма."""

from typing import TYPE_CHECKING, Optional

from telethon.events import common as events
from telethon.tl import types

if TYPE_CHECKING:
    import bot.models as models


async def is_superuser(event: events.EventCommon) -> bool:
    """Фильтр по суперюзеру."""
    user = await event.client.get_user(user_id=event.sender.id)
    return bool(user and user.is_superuser)


async def selected_chat(event: events.EventCommon) -> Optional['models.Channel']:
    """Фильтр чатов, которые сохранены в БД."""
    if isinstance(event.peer_id, types.PeerUser):
        chat_id = event.peer_id.user_id
    elif isinstance(event.peer_id, types.PeerChat):
        chat_id = event.peer_id.chat_id
    else:
        chat_id = event.peer_id.channel_id

    return await event.client.get_chat(chat_id=abs(chat_id))
