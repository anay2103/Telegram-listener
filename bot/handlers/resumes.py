from sqlalchemy_file.storage import StorageManager
from telethon import Button, events
from telethon.tl.types import DocumentAttributeFilename

from bot.exceptions import exception_handler
from bot.handlers.base import Commands


@exception_handler
@events.register(events.NewMessage(pattern=Commands.add_resume))
async def add_resume(event: events.NewMessage.Event) -> None:
    """Добавление резюме."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message('В ответном сообщении прикрепите файл резюме')
        response = await conv.get_response()
        filename = response.media.document.attributes[0].file_name
        content_type = response.media.document.mime_type
        content = await event.client.download_media(response, bytes)
        await event.client.cv_service.add_item(
            user_id=sender.id, filename=filename, content=content, content_type=content_type
        )
    await event.respond('Резюме добавлено!')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.get_resume))
async def get_resume(event: events.NewMessage.Event) -> None:
    """Просмотр резюме."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        resumes = await event.client.cv_service.show_user_resumes(sender.id)
        await event.respond(
            'Выберите резюме: ',
            buttons=[[Button.inline(r.name, data=r.name)] for r in resumes],
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        resume = await event.client.cv_service.filter_item(name=event.data.decode())
        file_id = resume.content['file_id']
        file = StorageManager.get_file(f'default/{file_id}')
        await event.client.send_file(sender, file.get_cdn_url(), attributes=[DocumentAttributeFilename(file.filename)])
        await event.answer()


@exception_handler
@events.register(events.NewMessage(pattern=Commands.delete_resume))
async def delete_resume(event: events.NewMessage.Event) -> None:
    """Удаление резюме."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        resumes = await event.client.cv_service.show_user_resumes(sender.id)
        await event.respond(
            'Выберите резюме, которое нужно удалить: ',
            buttons=[[Button.inline(r.name, data=r.id)] for r in resumes],
        )
        event = await conv.wait_event(events.CallbackQuery(sender))
        await event.client.cv_service.delete_item(_id=int(event.data.decode()))
        await event.respond('Резюме удалено.')
