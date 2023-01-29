from telethon import events


@events.register(events.NewMessage(pattern=r'/start'))
async def start(event):
    sender = await event.get_sender()
    await event.respond(
        f'Привет, {sender.username}! \n'
        'Для справки набери /help. \n'
        'Мой исходный код здесь: '
        '[https://github.com/anay2103/Telegram-listener](https://github.com/anay2103/Telegram-listener)',
        link_preview=False
    )


@events.register(events.NewMessage(pattern=r'/help'))
async def help(event):
    await event.respond(
        '/start - Начало диалога \n'
        '/help - Справка \n'
        '/Show_chats - Список чатов, в которых я могу искать слова \n'
        '/Add_keywords - Добавить слова для поиского запроса в чатах \n'
        '/Delete_keywords - Удалить слова из поискового запроса в чатах \n'
        '/Show_keywords - Показать слова поискового запроса'
    )
