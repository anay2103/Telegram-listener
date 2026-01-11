"""Main."""

import logging
from logging import config

from bot import handlers, settings
from bot.client import get_tg_client
from bot.filestorage import init_filestorage


def main():
    """Запуск бота и реального клиента. Бот общается с пользователями, клиент слушает чаты."""
    config.fileConfig('logging.conf')
    init_filestorage()
    client = get_tg_client()
    with client:
        client.add_event_handler(handlers.chats.chat_listener)
        for handler in handlers.BOT_HANDLERS:
            client.bot.add_event_handler(handler)
        client.bot.db_connect()
        client.bot.start(bot_token=settings.BOT_TOKEN)
        logging.info('Bot successfully started')
        client.loop.run_until_complete(client.disconnected)


if __name__ == '__main__':
    main()
