"""Сервис для работы с ChromaDB."""

from typing import Any, Dict, List, Optional

import chromadb


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
        metadatas: Optional[List[Dict[str, Any]]] = None,
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
