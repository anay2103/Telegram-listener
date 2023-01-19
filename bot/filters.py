"""Фильтры для сообщений Телеграма."""
from typing import TYPE_CHECKING

from telethon.events import common as events
from telethon.tl import types

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
    Фильтр чата, который есть в БД. ID чатов ТГ отрицательные, в БД сохраняются положительные.
    Метод обращается к атрибутам user_id, chat_id, channel_id в зависимости от типа ТГ чата.
    Сообщения из этих чатов преверяются на наличие ключевых слов.
    """
    if isinstance(event.peer_id, types.PeerUser):
        chat_id = event.peer_id.user_id
    elif isinstance(event.peer_id, types.PeerChat):
        chat_id = event.peer_id.chat_id
    else:
        chat_id = abs(event.peer_id.channel_id)

    session = event.client.db_session()
    chat = await ChannelRepository(session=session).get(id=abs(chat_id))
    await session.commit()
    return chat
