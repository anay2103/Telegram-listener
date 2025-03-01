"""Хэндлеры команд бота."""

import logging

from telethon import Button, errors, events
from telethon.tl.types import User as TLUser

from bot import filters
from bot.exceptions import exception_handler
from bot.handlers.base import Commands
from bot.schemas import Grades, Languages

FWD_TEXT = '**[Переслано из {chat_title}]**(https://t.me/c/{chat_id}/{message_id})\n\n{text}'
LANGUAGE_BUTTONS = [
    [Button.inline('Python', data=Languages.PYTHON.name)],
    [Button.inline('Golang', data=Languages.GOLANG.name)],
]
GRADE_BUTTONS = [
    [Button.inline('Junior', data=Grades.JUNIOR.name)],
    [Button.inline('Middle', data=Grades.MIDDLE.name)],
    [Button.inline('Senior', data=Grades.SENIOR.name)],
]


@events.register(events.NewMessage(func=filters.selected_chat))
async def chat_listener(event: events.NewMessage.Event) -> None:
    """Основной хэндлер, который слушает чаты.

    Если входящее сообщение подходит под запрос пользователя, оно пересылается пользователю.
    """
    chat = await event.get_chat()
    message = event.message
    recipients = await event.client.process_message(message.text)
    message.text = FWD_TEXT.format(
        chat_title=chat.username if isinstance(chat, TLUser) else chat.title,
        chat_id=chat.id,
        message_id=event.message.id,
        text=message.text,
    )
    # удаляем медиафайлы так как иначе получаем MediaCaptionTooLongError
    message.media = None

    if recipients:
        logging.info('Got message %s for sending', message.text)
    else:
        logging.info('Got message %s, skipping', message.text)
    for item in recipients:
        try:
            await event.client.bot.send_message(item.user_id, message)
        except errors.RPCError as err:
            logging.error('Error sending to recipient %s: %s', item.user_id, err, exc_info=True)
        else:
            logging.info('Sended  to recipient %s', item.user_id)


@exception_handler
@events.register(events.NewMessage(func=filters.is_superuser, pattern=Commands.add_chat))
async def add_chat(event: events.NewMessage.Event) -> None:
    """Добавление чата. Доступ только у суперюзера."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message(
            'Выберите категорию чата: ',
            buttons=LANGUAGE_BUTTONS,
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        language = event.data.decode().lower()
        await conv.send_message('В ответном сообщении введите название Телеграм-чата')
        response = await conv.get_response()
        chat_name = response.text
        try:
            chat_entity = await event.client.get_input_entity(chat_name)
        except ValueError:
            await conv.send_message(f'Чат не найден, проверьте название: {chat_name}')
        else:
            await event.client.add_chat(
                id=chat_entity.channel_id,
                language=language,
                name=chat_name,
            )
            await event.respond(f'Добавлен чат для поиска: {chat_name}')


@exception_handler
@events.register(events.NewMessage(func=filters.is_superuser, pattern=Commands.delete_chat))
async def delete_chat(event: events.NewMessage.Event) -> None:
    """Удаление чата. Доступ только у суперюзера."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        chats = await event.client.show_chats()
        await conv.send_message(
            'Выберите чат, который хотите удалить: ',
            buttons=[[Button.inline(f't.me/{chat.name}', data=chat.id)] for chat in chats],
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        chat_id = int(event.data.decode())
        await event.client.delete_chat(chat_id=chat_id)
        await event.respond('Чат успешно удален')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.show_chats))
async def show_chats(event: events.NewMessage.Event) -> None:
    """Общий список чатов, по которым осуществляется поиск."""
    chats = await event.client.show_chats()
    if not chats:
        return
    by_langs = dict.fromkeys(Languages, '')
    for chat in chats:
        by_langs[chat.language] += f't.me/{chat.name}\n'
    return await event.respond(
        '\n'.join([f'{lang.upper()}:\n{chats}' for lang, chats in by_langs.items()]),
        link_preview=False,
    )


@exception_handler
@events.register(events.NewMessage(pattern=Commands.add_filter))
async def add_filter(event: events.NewMessage.Event) -> None:
    """Добавление фильтра для поиска."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message(
            'Выберите язык для поиска вакансий: ',
            buttons=LANGUAGE_BUTTONS,
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        language = event.data.decode().lower()
        await event.respond(
            'Выберите грейд: ',
            buttons=GRADE_BUTTONS,
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        grade = event.data.decode()
        await event.client.create_searchitem(user_id=sender.id, grade=grade, language=language)
        await event.respond('Готово! Начинаем поиск.')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.show_my_filters))
async def show_filters(event: events.NewMessage.Event) -> None:
    """Список фильтров пользователя."""
    sender = await event.get_sender()
    results = await event.client.show_user_filters(sender.id)
    answer = '\n\n'.join([f'{result.language.name} - {result.grade.name}' for result in results])
    if answer:
        return await event.respond(answer)
    return await event.respond(f'Настройки пока не заполнены, введите команду {Commands.add_filter}')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.delete_filter))
async def delete_filter(event: events.NewMessage.Event) -> None:
    """Удаление фильтра для поиска."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        results = await event.client.show_user_filters(sender.id)
        if not results:
            return await event.respond(f'Настройки пока не заполнены, введите команду {Commands.add_filter}')
        await event.respond(
            'Выберите фильтр, который хотите удалить: ',
            buttons=[
                [Button.inline(f'{result.language.name} - {result.grade.name}', data=result.id)] for result in results
            ],
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        searchitem_id = int(event.data.decode())
        await event.client.delete_searchitem(searchitem_id=searchitem_id)
        return await event.respond('Фильтр успешно удален')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.delete_me))
async def delete_me(event: events.NewMessage.Event) -> None:
    """Удаление пользователя."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await event.respond(
            'Вы действительно хотите покинуть нас \U0001f97a?',
            buttons=[
                [Button.inline('Хочу остаться!', data='yes')],
                [Button.inline('Нет, исключите меня из рассылки', data='no')],
            ],
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        response = event.data.decode()
        if response == 'no':
            await event.client.delete_user(user_id=sender.id)
            return await event.respond('Вы успешно исключены из списка рассылки. Желаем удачи!')
        await event.respond('Ура! Вы решили остаться с нами!')
