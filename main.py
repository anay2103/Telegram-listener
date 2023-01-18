from telethon.sessions import StringSession

import bot.handlers as handlers
import bot.settings as settings
from bot.mixins import Client

bot = Client(session=settings.BOT_NAME, api_id=settings.API_ID, api_hash=settings.API_HASH)
client = Client(StringSession(settings.CLIENT_SESSION), settings.API_ID, settings.API_HASH)


def main():
    """Запуск бота и реального клиента. Бот общается с пользователями, клиент слушает чаты."""
    for handler in handlers.BOT_HANDLERS:
        bot.add_event_handler(handler)
    bot.db_connect()
    bot.start(bot_token=settings.BOT_TOKEN)

    with client:
        client.db_connect()
        client.add_event_handler(handlers.chat_listener)
        client.loop.run_forever()


if __name__ == '__main__':
    main()
