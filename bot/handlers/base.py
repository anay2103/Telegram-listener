"""Базовые команды бота."""
from enum import Enum
from telethon import events


class Commands(str, Enum):
    """Команды бота."""

    start = '/start'
    help = '/help'
    add_chat = '/add_chat'
    delete_chat = '/delete_chat'
    show_chats = '/show_chats'
    add_grade = '/add_grade'
    show_grade = '/show_grade'


@events.register(events.NewMessage(pattern=Commands.start))
async def start(event):
    sender = await event.get_sender()
    await event.respond(
        f'Привет, {sender.username}! \n'
        'Для справки набери /help. \n'
        'Мой исходный код здесь: '
        '[https://github.com/anay2103/Telegram-listener](https://github.com/anay2103/Telegram-listener)',
        link_preview=False
    )


@events.register(events.NewMessage(pattern=Commands.help))
async def help(event):
    await event.respond(
        f'{Commands.start} - Start me! \n'
        f'{Commands.help} - Справка \n'
        f'{Commands.show_chats} - Список чатов для поиска \n'
        f'{Commands.add_grade} - Добавить грейд вакансии для поиска \n'
        f'{Commands.show_grade} - Показать мой текущий грейд для поиска'
    )
