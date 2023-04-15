"""Базовые команды бота."""
from enum import Enum
from telethon import events


class Commands(str, Enum):
    """Команды бота."""

    start = '/start'
    help = '/help'
    add_chat = '/add_chat'
    show_chats = '/show_chats'
    add_keyword = '/add_keyword'
    show_keywords = '/show_keywords'
    delete_keywords = '/delete_keyword'
    # инлайн-команды
    start_search = 'Начать поиск'


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
        f'{Commands.add_keyword} - Добавить слова для поиского запроса в чатах \n'
        f'{Commands.delete_keywords} - Удалить слова из поискового запроса в чатах \n'
        f'{Commands.show_keywords} - Показать слова поискового запроса'
    )
