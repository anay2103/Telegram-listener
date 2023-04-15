"""Хэндлеры команд бота."""
import json

from telethon import Button, events
from telethon.tl.types import User as TLUser

from bot import crud, filters, schemas
from bot.exceptions import bot_exceptions
from bot.handlers.base import Commands

FWD_TEXT = '**[Переслано из {chat_title}]**(https://t.me/c/{chat_id}/{message_id})\n\n{text}'


@events.register(events.NewMessage(func=filters.selected_chat))
async def chat_listener(event: events.NewMessage.Event) -> None:
    """Основной хэндлер, который слушает чаты.

    Если входящее сообщение подходит под запрос пользователя, оно пересылается пользователю.
    """
    chat = await event.get_chat()
    message = event.message
    session = event.client.db_session
    users = crud.UserRepository(session).apply_query(message.text)
    message.text = FWD_TEXT.format(
        chat_title=chat.username if isinstance(chat, TLUser) else chat.title,
        chat_id=chat.id,
        message_id=event.message.id,
        text=message.text,
    )
    # удаляем медиафайлы так как иначе получаем MediaCaptionTooLongError
    # TODO: возможно есть способы обхода
    message.media = None
    async for user in users:
        await event.client.bot.send_message(user.id, message)


@bot_exceptions
@events.register(events.NewMessage(func=filters.is_superuser, pattern=Commands.add_chat))
async def add_chat(event: events.NewMessage.Event) -> None:
    """Добавление чата. Доступ только у суперюзера."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message('В ответном сообщении введите название Телеграм-чата')
        chat = (await conv.get_response()).text
        try:
            chat_entity = await event.client.get_input_entity(chat)
        except ValueError:
            await event.respond(f'Чат не найден, проверьте название: {chat}')
        else:
            session = event.client.db_session
            await crud.ChannelRepository(session).add(id=chat_entity.channel_id, name=chat)
            await event.respond(f'Добавлен чат для поиска: {chat}')


@bot_exceptions
@events.register(events.NewMessage(pattern=Commands.show_chats))
async def show_chats(event: events.NewMessage.Event) -> None:
    """Общий список чатов, по которым осуществляется поиск."""
    session = event.client.db_session
    chats = await crud.ChannelRepository(session).list()
    await event.respond(
        '\n'.join([f't.me/{chat.name}' for chat in chats]),
        link_preview=False,
    )


@bot_exceptions
@events.register(events.NewMessage(pattern=Commands.add_keyword))
async def add_keywords(event: events.NewMessage.Event) -> None:
    """Добавление ключевых слов для поиска."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message('В ответном сообщении введите слово или слово словосочетание для поиска')
        await event.client.set_state(sender.id, filters.State.adding)
        word = (await conv.get_response()).text
        await conv.send_message(
            f'Введите тип для ключевого слова: {word.upper()}',
            buttons=[
                Button.inline(
                    'обязательно', data=schemas.Keyword(name=word, mode=schemas.KeywordModes.binding).json()
                    ),
                Button.inline(
                    'опционально', data=schemas.Keyword(name=word, mode=schemas.KeywordModes.optional).json()
                    ),
                Button.inline(
                    'исключить', data=schemas.Keyword(name=word, mode=schemas.KeywordModes.negative).json()
                    ),
            ],
        )


@bot_exceptions
@events.register(events.CallbackQuery(func=filters.is_adding))
async def adding_callback(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для добавления пользователем ключевого слова."""
    kwd = schemas.Keyword(**json.loads(event.data.decode()))
    sender = await event.get_sender()
    session = event.client.db_session
    await crud.KeywordRepository(session).add(kwd.name, kwd.mode, sender.id)
    await event.respond(
        f'Добавлено ключевое слово: {kwd.name}',
        buttons=[Button.text('Начать поиск', resize=True, single_use=True)]
    )


@bot_exceptions
@events.register(events.NewMessage(pattern=Commands.start_search))
async def start_search(event: events.NewMessage.Event) -> None:
    """Запуск поиска по ключевым словам."""
    sender = await event.get_sender()
    session = event.client.db_session
    await crud.UserRepository(session).make_query(sender.id)

    await event.client.set_state(sender.id, None)
    await event.client.send_message(sender, 'Слова отредактированы! Начинаем поиск.', buttons=Button.clear())


@bot_exceptions
@events.register(events.NewMessage(pattern=Commands.show_keywords))
async def show_keywords(event: events.NewMessage.Event) -> None:
    """Список ключевых слов пользователя."""
    sender = await event.get_sender()
    session = event.client.db_session
    keywords = await crud.KeywordRepository(session).get(sender.id)
    await event.respond(''.join([f'{kwd.name.upper()} - {kwd.mode}\n' for kwd in keywords]))


@bot_exceptions
@events.register(events.NewMessage(pattern=Commands.delete_keywords))
async def delete_keywords(event: events.NewMessage.Event) -> None:
    """Удаление ключевых слов пользователя."""
    sender = await event.get_sender()
    session = event.client.db_session
    await event.client.set_state(sender.id, filters.State.deleting)
    keywords = await crud.KeywordRepository(session).get(sender.id)
    buttons = [
        [Button.inline(f'{kwd.name}', data=schemas.KeywordName(kwd.name))]
        for kwd in keywords
    ]
    await event.respond('Выберите слова для удаления', buttons=buttons)


@bot_exceptions
@events.register(events.CallbackQuery(func=filters.is_deleting))
async def deleting_callback(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для удаления пользователем ключевого слова."""
    kwd = schemas.KeywordName(event.data.decode())
    sender = await event.get_sender()
    session = event.client.db_session
    await crud.KeywordRepository(session).delete(name=kwd, user_id=sender.id)
    await event.respond(
        f'Удалены ключевые слова: {kwd.upper()}',
        buttons=[Button.text(Commands.start_search, resize=True, single_use=True)]
    )
