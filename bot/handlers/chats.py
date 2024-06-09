"""Хэндлеры команд бота."""
import logging
import re
from functools import partial

from telethon import Button, errors, events
from telethon.tl.types import User as TLUser

from bot import crud, filters
from bot.schemas import (
    ChannelAdminState,
    ChoosingGradeState,
    Grades,
)
from bot.exceptions import exception_handler
from bot.handlers.base import Commands

FWD_TEXT = '**[Переслано из {chat_title}]**(https://t.me/c/{chat_id}/{message_id})\n\n{text}'


@events.register(events.NewMessage(func=filters.selected_chat))
async def chat_listener(event: events.NewMessage.Event) -> None:
    """Основной хэндлер, который слушает чаты.

    Если входящее сообщение подходит под запрос пользователя, оно пересылается пользователю.
    """
    chat = await event.get_chat()
    message = event.message
    recipients = await event.client.process(message.text)
    message.text = FWD_TEXT.format(
        chat_title=chat.username if isinstance(chat, TLUser) else chat.title,
        chat_id=chat.id,
        message_id=event.message.id,
        text=message.text,
    )
    # удаляем медиафайлы так как иначе получаем MediaCaptionTooLongError
    # TODO: возможно есть способы обхода
    message.media = None

    if recipients:
        logging.info('Got message %s for sending', message.text)
    else:
        logging.info('Got message %s, skipping', message.text)
    for user in recipients:
        try:
            await event.client.bot.send_message(user.id, message)
        except errors.RPCError as err:
            logging.error('Error sending to recipient %s: %s', user.id, err, exc_info=True)
        else:
            logging.info('Sended  to recipient %s', user.id)


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
        await event.client.channel_repository.add(id=chat_entity.channel_id, name=chat_name)
        await event.respond(f'Добавлен чат для поиска: {chat_name}')

    sender = await event.get_sender()
    await event.client.set_state(sender.id, None)


@exception_handler
@events.register(events.NewMessage(func=filters.is_superuser, pattern=Commands.delete_chat))
async def delete_chat(event: events.NewMessage.Event) -> None:
    """Удаление чата. Доступ только у суперюзера."""
    sender = await event.get_sender()
    chats = await event.client.channel_repository.list()
    await event.client.set_state(sender.id, ChannelAdminState.deleting_channel)
    await event.respond(
        'Выберите чат, который хотите удалить: ',
        buttons=[
            [Button.inline(f't.me/{chat.name}', data=chat.id)] for chat in chats
        ]
    )


@exception_handler
@events.register(events.CallbackQuery(func=partial(filters.filter_status, status=ChannelAdminState.deleting_channel)))
async def deleting_chat_callback(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для удаления чата."""
    chat_id = int(event.data.decode())
    await event.client.channel_repository.delete(id=chat_id)
    sender = await event.get_sender()
    await event.client.set_state(sender.id, None)
    await event.respond('Чат успешно удален')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.show_chats))
async def show_chats(event: events.NewMessage.Event) -> None:
    """Общий список чатов, по которым осуществляется поиск."""
    chats = await event.client.channel_repository.list()
    if chats:
        return await event.respond(
            '\n'.join([f't.me/{chat.name}' for chat in chats]),
            link_preview=False,
        )
    await event.respond('Пока не добавлено ни одного чата')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.add_grade))
async def add_grade(event: events.NewMessage.Event) -> None:
    """Добавление грейда для поиска."""
    sender = await event.get_sender()
    await event.client.set_state(sender.id, ChoosingGradeState.сhoosing_grade)
    await event.respond(
        'Выберите грейд: ',
        buttons=[
            [Button.inline('Junior', data=Grades.JUNIOR.name)],
            [Button.inline('Middle', data=Grades.MIDDLE.name)],
            [Button.inline('Senior', data=Grades.SENIOR.name)],
        ],
    )


@exception_handler
@events.register(events.CallbackQuery(func=partial(filters.filter_status, status=ChoosingGradeState.сhoosing_grade)))
async def choosing_grade(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для выбора грейда."""
    grade = event.data.decode()
    if grade not in Grades.choices():
        raise ValueError('Недопустимое значение грейда')
    sender = await event.get_sender()
    await event.client.user_repository.update(id=sender.id, grade=grade)
    await event.client.set_state(sender.id, ChoosingGradeState.choosing_no_grade_ok)
    await event.respond(
        'Присылать вакансии без указания грейда?',
        buttons=[
            [Button.inline('Да', data='yes')],
            [Button.inline('Нет', data='no')],
        ],
    )


@exception_handler
@events.register(events.CallbackQuery(
    data=re.compile('yes|no'),
    func=partial(filters.filter_status, status=ChoosingGradeState.choosing_no_grade_ok)
))
async def choosing_no_grade_ok(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для выбора подписки на вакансии без указания грейда."""
    no_grade_data = event.data.decode()
    sender = await event.get_sender()
    no_grade_ok = True if no_grade_data == 'yes' else False
    await event.client.user_repository.update(id=sender.id, no_grade_ok=no_grade_ok)
    await event.client.set_state(sender.id, None)
    await event.respond('Готово! Начинаем поиск.', buttons=Button.clear())


@exception_handler
@events.register(events.NewMessage(pattern=Commands.show_grade))
async def show_grade(event: events.NewMessage.Event) -> None:
    """Настройки пользователя."""
    sender = await event.get_sender()
    session = event.client.db_session
    user = await crud.UserRepository(session).get(sender.id)
    if user:
        search_no_grade = u'\u2705' if user.no_grade_ok is True else u'\u274C'
        grade_answer = f'Грейд для поиска - {user.grade},\nПоиск вакансий без указания грейда - {search_no_grade}'
    else:
        grade_answer = f'Ваш грейд пока не заполнен, введите команду {Commands.add_grade}'
    await event.respond(grade_answer)


@exception_handler
@events.register(events.NewMessage(pattern=Commands.delete_grade))
async def delete_grade(event: events.NewMessage.Event) -> None:
    """Удаление грейда для поиска."""
    sender = await event.get_sender()
    await event.client.set_state(sender.id, ChoosingGradeState.deleting_grade)
    await event.respond(
        'Вы действительно не хотите оставаться с нами?',
        buttons=[
            [Button.inline('Хочу остаться!', data='yes')],
            [Button.inline('Нет, исключите меня из рассылки', data='no')],
        ],
    )


@exception_handler
@events.register(events.CallbackQuery(func=partial(filters.filter_status, status=ChoosingGradeState.deleting_grade)))
async def deleting_grade(event: events.CallbackQuery.Event) -> None:
    """Коллбэк для удаления грейда."""
    response = event.data.decode()
    sender = await event.get_sender()
    await event.client.set_state(sender.id, None)
    if response == 'no':
        await event.client.user_repository.delete(id=sender.id)
        return await event.respond('Вы успешно исключены из списка рассылки. Желаем удачи!', buttons=Button.clear())
    await event.respond('Ура! Вы решили остаться с нами!', buttons=Button.clear())
