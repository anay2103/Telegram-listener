"""Сервис для работы с ChromaDB."""

from typing import Any, List, Optional

import chromadb
from chromadb import GetResult

from bot.chromadb.client import get_chromadb_collection


class ChromaService:
    """Сервис для работы с коллекцией ChromaDB."""

    def __init__(self, collection: chromadb.Collection) -> None:
        """Инициализация сервиса.

        Args:
            collection: Объект коллекции ChromaDB
        """
        self.collection = collection

    def upsert(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[dict[str, Any]]] = None,
    ) -> None:
        """Добавление или обновление документов в коллекции.

        Args:
            ids: Список уникальных идентификаторов документов
            documents: Список текстов документов
            metadatas: Опциональный список метаданных для документов
        """
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    def get(
        self,
        ids: Optional[List[str]] = None,
        *,
        where: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include: Optional[List[str]] = None,
    ) -> GetResult:
        """Получение документов из коллекции.

        Args:
            ids: Опциональный список идентификаторов документов для получения
            limit: Опциональный лимит количества возвращаемых документов
            offset: Опциональный offset для пагинации
            include: Опциональный список полей для включения в ответ.
                     Может содержать: 'documents', 'metadatas', 'embeddings', 'distances'

        Returns:
            список ChromaResult с результатами запроса
        """
        kwargs: dict[str, Any] = {}
        if ids is not None:
            kwargs['ids'] = ids
        if where is not None:
            kwargs['where'] = where
        if limit is not None:
            kwargs['limit'] = limit
        if offset is not None:
            kwargs['offset'] = offset
        if include is not None:
            kwargs['include'] = include

        return self.collection.get(**kwargs)


def get_chromadb_service(collection_name: str) -> ChromaService:
    collection = get_chromadb_collection(name=collection_name)
    return ChromaService(collection)
