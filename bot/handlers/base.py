"""Базовые команды бота."""

from enum import StrEnum

from telethon import events


class Commands(StrEnum):
    """Команды бота."""

    start = '/start'
    help = '/help'
    add_chat = '/add_chat'
    delete_chat = '/delete_chat'
    show_chats = '/show_chats'
    add_filter = '/add_filter'
    show_my_filters = '/show_my_filters'
    delete_filter = '/delete_filter'
    delete_me = '/delete_me'


@events.register(events.NewMessage(pattern=Commands.start))
async def start(event):
    sender = await event.get_sender()
    await event.respond(
        f'Привет, {sender.username}! \n'
        'Для справки набери /help. \n'
        'Мой исходный код здесь: '
        '[https://github.com/anay2103/Telegram-listener](https://github.com/anay2103/Telegram-listener)',
        link_preview=False,
    )


@events.register(events.NewMessage(pattern=Commands.help))
async def help(event):
    await event.respond(
        f'{Commands.start} - Start me! \n'
        f'{Commands.help} - Справка \n'
        f'{Commands.show_chats} - Список чатов для поиска \n'
        f'{Commands.add_filter} - Добавить фильтр для поиска вакансий \n'
        f'{Commands.show_my_filters} - Показать мои фильтры для поиска вакансий \n'
        f'{Commands.delete_filter} - Удалить фильтр поиска вакансий\n'
        f'{Commands.delete_me} - Удалить мои данные полностью'
    )
