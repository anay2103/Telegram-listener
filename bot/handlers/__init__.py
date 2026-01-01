from . import base, chats, resumes

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
    resumes.add_resume,
    resumes.get_resume,
    resumes.delete_resume,
]
