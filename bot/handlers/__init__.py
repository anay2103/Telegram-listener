from . import base
from . import chats

BOT_HANDLERS = [
    base.help,
    base.start,
    chats.show_filters,
    chats.add_filter,
    chats.choose_language_callback,
    chats.choose_grade_callback,
    chats.add_chat,
    chats.adding_chat_callback,
    chats.delete_filter,
    chats.delete_filter_callback,
    chats.show_chats,
    chats.delete_chat,
    chats.deleting_chat_callback,
    chats.delete_me,
    chats.deleting_me_callback,
]
