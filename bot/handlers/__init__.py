from .base import help, start
from .chats import (add_chat, add_keywords, chat_listener,  # noqa: F401
                    delete_keywords, show_chat, show_keywords)

BOT_HANDLERS = [start, help, add_chat, show_chat, add_keywords, show_keywords, delete_keywords]
