from . import base, chats, prompts, resumes

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
    prompts.get_job_description,
    prompts.add_job_description,
    prompts.update_job_description,
    prompts.delete_job_description,
]
