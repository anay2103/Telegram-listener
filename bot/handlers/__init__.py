from . import base
from . import chats

BOT_HANDLERS = [
    base.help,
    base.start,
    chats.add_chat,
    chats.show_chats,
    chats.start_search,
    chats.add_keywords,
    chats.show_keywords,
    chats.delete_keywords,
    chats.adding_callback,
    chats.deleting_callback,
]
