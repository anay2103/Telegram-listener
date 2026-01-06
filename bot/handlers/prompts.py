import uuid
from datetime import datetime

from telethon import events

from bot.chromadb.client import get_chromadb_collection
from bot.chromadb.service import ChromaService
from bot.exceptions import exception_handler
from bot.handlers.base import Commands


@exception_handler
@events.register(events.NewMessage(pattern=Commands.add_job_description))
async def add_job_description(event: events.NewMessage.Event) -> None:
    """Добавление описания желаемой вакансии."""
    sender = await event.get_sender()
    async with event.client.conversation(sender) as conv:
        await conv.send_message('В ответном сообщении опишите желаемую вакансию')
        response = await conv.get_response()
        job_description_text = response.text.strip()

        if not job_description_text:
            return await event.respond('Описание вакансии не может быть пустым')

        collection = get_chromadb_collection('bot_queries')
        chroma_service = ChromaService(collection)

        query_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Сохраняем описание в ChromaDB
        chroma_service.upsert(
            ids=[query_id],
            documents=[job_description_text],
            metadatas=[
                {
                    'user_id': sender.id,
                    'username': sender.username or '',
                    'created_at': timestamp,
                }
            ],
        )

    return await event.respond('Описание вакансии сохранено!')
