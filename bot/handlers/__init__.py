from . import base, chats

BOT_HANDLERS = [
    base.help,
    base.start,
    chats.show_filters,
    chats.show_chats,
    chats.add_filter,
    chats.add_chat,
    chats.delete_filter,
    chats.delete_chat,
    chats.delete_me,
]
