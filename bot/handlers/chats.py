"""Хэндлеры команд бота."""

import logging
from functools import partial

from telethon import Button, errors, events
from telethon.tl.types import User as TLUser

from bot import filters
from bot.exceptions import exception_handler
from bot.handlers.base import Commands
from bot.schemas import (
    ChannelAdminState,
    Grades,
    Languages,
    UserState,
)

FWD_TEXT = '**[Переслано из {chat_title}]**(https://t.me/c/{chat_id}/{message_id})\n\n{text}'


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
    await event.respond('В ответном сообщении введите название Телеграм-чата')
    await event.client.set_state(sender.id, ChannelAdminState.adding_channel)
    event.message = None


@exception_handler
@events.register(events.NewMessage(func=partial(filters.filter_status, status=ChannelAdminState.adding_channel)))
async def adding_chat_callback(event: events.NewMessage.Event) -> None:
    """Коллбэк для добавления чата."""
    chat_name = event.message.text
    try:
        chat_entity = await event.client.get_input_entity(chat_name)
    except ValueError:
        await event.respond(f'Чат не найден, проверьте название: {chat_name}')
    else:
        await event.client.add_chat(id=chat_entity.channel_id, name=chat_name)
        await event.respond(f'Добавлен чат для поиска: {chat_name}')

    sender = await event.get_sender()
    await event.client.set_state(sender.id, None)


@exception_handler
@events.register(events.NewMessage(func=filters.is_superuser, pattern=Commands.delete_chat))
async def delete_chat(event: events.NewMessage.Event) -> None:
    """Удаление чата. Доступ только у суперюзера."""
    sender = await event.get_sender()
    chats = await event.client.show_chats()
    await event.client.set_state(sender.id, ChannelAdminState.deleting_channel)
    await event.respond(
        'Выберите чат, который хотите удалить: ',
        buttons=[[Button.inline(f't.me/{chat.name}', data=chat.id)] for chat in chats],
    )


@exception_handler
@events.register(events.CallbackQuery(func=partial(filters.filter_status, status=ChannelAdminState.deleting_channel)))
async def deleting_chat_callback(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для удаления чата."""
    chat_id = int(event.data.decode())
    await event.client.delete_chat(chat_id=chat_id)
    sender = await event.get_sender()
    await event.client.set_state(sender.id, None)
    await event.respond('Чат успешно удален')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.show_chats))
async def show_chats(event: events.NewMessage.Event) -> None:
    """Общий список чатов, по которым осуществляется поиск."""
    chats = await event.client.show_chats()
    if chats:
        return await event.respond(
            '\n'.join([f't.me/{chat.name}' for chat in chats]),
            link_preview=False,
        )
    await event.respond('Пока не добавлено ни одного чата')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.add_filter))
async def add_filter(event: events.NewMessage.Event) -> None:
    """Добавление фильтра для поиска."""
    await event.respond(
        'Выберите язык для поиска вакансий: ',
        buttons=[
            [Button.inline('Python', data=Languages.PYTHON.name)],
            [Button.inline('Golang', data=Languages.GO.name)],
        ],
    )


@exception_handler
@events.register(events.CallbackQuery(func=filters.choosing_language))
async def choose_language_callback(event: events.CallbackQuery.Event) -> None:
    """Добавление грейда для поиска."""
    sender = await event.get_sender()
    language = event.data.decode()
    if language not in Languages._member_names_:
        raise ValueError('Недопустимое значение')
    await event.client.set_state(sender.id, data={'language': language})
    await event.respond(
        'Выберите грейд: ',
        buttons=[
            [Button.inline('Junior', data=Grades.JUNIOR.name)],
            [Button.inline('Middle', data=Grades.MIDDLE.name)],
            [Button.inline('Senior', data=Grades.SENIOR.name)],
        ],
    )


@exception_handler
@events.register(events.CallbackQuery(func=filters.choosing_grade))
async def choose_grade_callback(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для выбора грейда."""
    grade = event.data.decode()
    if grade not in Grades._member_names_:
        raise ValueError('Недопустимое значение грейда')
    sender = await event.get_sender()
    data = await event.client.get_state(sender.id)
    language = data.get('language')
    if not language:
        raise ValueError('Ошибка, попробуйте еще раз')
    await event.client.create_searchitem(user_id=sender.id, grade=grade, language=language)
    await event.client.set_state(sender.id, None)
    await event.respond('Готово! Начинаем поиск.', buttons=Button.clear())


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
    await event.client.set_state(sender.id, UserState.deleting_filter)
    results = await event.client.show_user_filters(sender.id)
    await event.respond(
        'Выберите фильтр, который хотите удалить: ',
        buttons=[
            [Button.inline(f'{result.language.name} - {result.grade.name}', data=result.id)] for result in results
        ],
    )


@exception_handler
@events.register(events.CallbackQuery(func=partial(filters.filter_status, status=UserState.deleting_filter)))
async def delete_filter_callback(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для удаления фильтра."""
    searchitem_id = int(event.data.decode())
    sender = await event.get_sender()
    await event.client.delete_searchitem(searchitem_id=searchitem_id)
    await event.client.set_state(sender.id, None)
    return await event.respond('Фильтр успешно удален')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.delete_me))
async def delete_me(event: events.NewMessage.Event) -> None:
    """Удаление пользователя."""
    sender = await event.get_sender()
    await event.client.set_state(sender.id, UserState.deleting_me)
    await event.respond(
        'Вы действительно хотите покинуть нас \U0001f97a?',
        buttons=[
            [Button.inline('Хочу остаться!', data='yes')],
            [Button.inline('Нет, исключите меня из рассылки', data='no')],
        ],
    )


@exception_handler
@events.register(events.CallbackQuery(func=partial(filters.filter_status, status=UserState.deleting_me)))
async def deleting_me_callback(event: events.CallbackQuery.Event) -> None:
    response = event.data.decode()
    sender = await event.get_sender()
    if response == 'no':
        await event.client.delete_user(user_id=sender.id)
        return await event.respond('Вы успешно исключены из списка рассылки. Желаем удачи!', buttons=Button.clear())
    await event.respond('Ура! Вы решили остаться с нами!', buttons=Button.clear())
