from telethon import Button, events

import bot.filters as filters
import bot.repository as repository
from bot.event_parser import MessageParser

BUTTONS = [
    Button.text('Add keywords', resize=True),
    Button.text('Show keywords', resize=True),
    Button.text('Delete keywords', resize=True),
]
THRESHOLD = 0.02


@events.register(events.NewMessage(func=filters.selected_chat))
async def chat_listener(event):
    session = event.client.db_session()
    users = await repository.UserRepository(session).list()
    await session.commit()
    user_ranks = MessageParser(session, event.raw_text).get_ts_rank(users)
    async for user, rank in user_ranks:
        if rank > THRESHOLD:  # пороговое значение взято пока на глаз
            await event.client.bot.send_message(user.id, f'Для вас сообщение: {event.message.text}')


@events.register(events.NewMessage(func=filters.is_superuser, pattern=r'add_chat.+'))
async def add_chat(event) -> None:
    """Добавление чата. Доступ только у суперюзера."""
    chat_name = event.raw_text.lstrip('add_chat')
    try:
        chat_entity = await event.client.get_input_entity(chat_name)
    except ValueError:
        await event.respond(f'Чат не найден, проверьте название: {chat_name}')
        return
    session = event.client.db_session()
    await repository.ChannelRepository(session).add(chat_entity.channel_id, chat_name)
    await session.commit()
    await event.respond(f'Добавлен чат для поиска: {chat_name}')


@events.register(events.NewMessage(pattern=r'Show chats'))
async def show_chat(event) -> None:
    """Общий список чатов, по которым осуществляется поиск."""
    session = event.client.db_session()
    chats = await repository.ChannelRepository(session).list()
    await session.commit()
    await event.respond(', '.join([chat.name for chat in chats]), buttons=BUTTONS)


@events.register(events.NewMessage(pattern=r'Add keywords'))
async def add_keywords(event) -> None:
    """Добавление ключевых слов для поиска."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message('В ответном сообщении введите ключевые слова для поиска')
        response = await conv.get_response()
        session = event.client.db_session()
        await repository.KeywordRepository(session).add(response.text.split(), sender)
        await session.commit()

        await event.client.send_message(
            sender,
            f'Добавлены ключевые слова: {response.text}',
            buttons=BUTTONS,
        )


@events.register(events.NewMessage(pattern=r'Show keywords'))
async def show_keywords(event):
    """Список ключевых слов для пользователя."""
    sender = await event.get_sender()
    session = event.client.db_session()
    user = await repository.UserRepository(session).get(id=sender.id)
    await session.commit()
    await event.respond(
        ', '.join([keyword.name for keyword in user.keywords]),
        buttons=BUTTONS,
    )


@events.register(events.NewMessage(pattern=r'Delete keywords'))
async def delete_keywords(event):
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message('В ответном сообщении введите ключевые слова, которые нужно удалить')
        response = await conv.get_response()
        session = event.client.db_session()
        try:
            await repository.KeywordRepository(session).delete(response.text.split(), sender)
        except repository.StoreException as error:
            await event.client.send_message(sender, str(error), buttons=BUTTONS)
        else:
            await session.commit()
            await event.client.send_message(
                sender,
                f'Удалены ключевые слова: {response.text}',
                buttons=BUTTONS,
            )

BOT_HANDLERS = [add_chat, show_chat, add_keywords, show_keywords, delete_keywords]
