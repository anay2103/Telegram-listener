"""Main."""
from telethon.sessions import StringSession

from bot import handlers, settings
from bot.client import Client


bot = Client(
    session=settings.BOT_NAME,
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
)
client = Client(
    session=StringSession(settings.CLIENT_SESSION),
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot=bot,
)


def main():
    """Запуск бота и реального клиента. Бот общается с пользователями, клиент слушает чаты."""
    with client:
        client.db_connect()
        client.add_event_handler(handlers.chats.chat_listener)
        for handler in handlers.BOT_HANDLERS:
            client.bot.add_event_handler(handler)
        client.bot.db_connect()
        client.bot.redis_connect()
        client.bot.start(bot_token=settings.BOT_TOKEN)

        client.loop.run_forever()


if __name__ == '__main__':
    main()
