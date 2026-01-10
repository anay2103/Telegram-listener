import uuid
from datetime import datetime

from telethon import Button, events

from bot.chromadb.client import get_chromadb_collection
from bot.chromadb.service import ChromaService
from bot.exceptions import exception_handler
from bot.handlers.base import Commands


@exception_handler
@events.register(events.NewMessage(pattern=Commands.get_job_description))
async def get_job_description(event: events.NewMessage.Event) -> None:
    """Получение сохраненного описания желаемой вакансии."""
    sender = await event.get_sender()

    collection = get_chromadb_collection('bot_queries')
    chroma_service = ChromaService(collection)

    result = chroma_service.get(
        where={'user_id': {'$eq': sender.id}},
        include=['documents', 'metadatas'],
        limit=1,
    )

    if not result['ids'] or len(result['ids']) == 0:
        return await event.respond(
            'У вас нет сохраненного описания вакансии. Используйте /add_job_description для создания.'
        )

    saved_text = result['documents'][0] if result['documents'] else ''

    if not saved_text:
        return await event.respond('Сохраненное описание вакансии пустое.')

    return await event.respond(f'Ваше сохраненное описание вакансии:\n\n{saved_text}')


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


@exception_handler
@events.register(events.NewMessage(pattern=Commands.update_job_description))
async def update_job_description(event: events.NewMessage.Event) -> None:
    """Обновление описания желаемой вакансии."""
    sender = await event.get_sender()

    collection = get_chromadb_collection('bot_queries')
    chroma_service = ChromaService(collection)

    # Ищем сохраненные запросы пользователя по user_id в метаданных
    result = chroma_service.get(
        where={'user_id': {'$eq': sender.id}},
        include=['documents', 'metadatas'],
        limit=1,
    )

    # GetResult можно использовать как словарь
    if not result['ids'] or len(result['ids']) == 0:
        return await event.respond(
            'У вас нет сохраненного описания вакансии. Используйте /add_job_description для создания.'
        )

    # Берем первый найденный запрос
    query_id = result['ids'][0]
    old_text = result['documents'][0] if result['documents'] else ''
    old_metadata = result['metadatas'][0] if result['metadatas'] else {}

    async with event.client.conversation(sender) as conv:
        await conv.send_message(f'Ваше текущее описание вакансии:\n\n{old_text}\n\nПришлите новый текст для замены:')
        response = await conv.get_response()
        new_text = response.text.strip()

        if not new_text:
            return await event.respond('Новый текст не может быть пустым')

        # Обновляем запись в ChromaDB (используем тот же ID для обновления)
        new_metadata = old_metadata.copy()
        new_metadata['created_at'] = datetime.now().isoformat()

        chroma_service.upsert(
            ids=[query_id],
            documents=[new_text],
            metadatas=[new_metadata],
        )

    return await event.respond('Описание вакансии обновлено!')


@exception_handler
@events.register(events.NewMessage(pattern=Commands.delete_job_description))
async def delete_job_description(event: events.NewMessage.Event) -> None:
    """Удаление описания желаемой вакансии."""
    sender = await event.get_sender()

    collection = get_chromadb_collection('bot_queries')
    chroma_service = ChromaService(collection)

    # Ищем сохраненные запросы пользователя по user_id в метаданных
    result = chroma_service.get(
        where={'user_id': {'$eq': sender.id}},
        include=['documents', 'metadatas'],
        limit=1,
    )

    if not result['ids'] or len(result['ids']) == 0:
        return await event.respond('У вас нет сохраненного описания вакансии.')

    # Берем первый найденный запрос
    query_id = result['ids'][0]
    old_text = result['documents'][0] if result['documents'] else ''

    async with event.client.conversation(sender) as conv:
        await conv.send_message(
            f'Ваше сохраненное описание вакансии:\n\n{old_text}\n\nВы уверены, что хотите удалить это описание?',
            buttons=[
                [Button.inline('Да', data=f'delete_yes_{query_id}'), Button.inline('Нет', data=f'delete_no_{query_id}')]
            ],
        )
        callback_event = await conv.wait_event(events.CallbackQuery(sender))
        callback_data = callback_event.data.decode()

        if callback_data.startswith('delete_yes_'):
            # Извлекаем query_id из callback_data (формат: delete_yes_{query_id})
            extracted_query_id = callback_data[len('delete_yes_') :]
            # Удаляем запрос из ChromaDB
            collection.delete(ids=[extracted_query_id])
            await callback_event.answer('Описание вакансии удалено!')
            return await callback_event.respond('Описание вакансии удалено!')
        else:
            # Пользователь нажал "Нет" или другое
            await callback_event.answer('Удаление отменено.')
            return await callback_event.respond('Удаление отменено.')
