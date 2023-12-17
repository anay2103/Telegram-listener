from . import base
from . import chats

BOT_HANDLERS = [
    base.help,
    base.start,
    chats.add_chat,
    chats.show_chats,
    chats.delete_chat,
    chats.adding_chat_callback,
    chats.deleting_chat_callback,
    chats.add_grade,
    chats.show_grade,
    chats.choosing_grade,
    chats.choosing_no_grade_ok,
]
