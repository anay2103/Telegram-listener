from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncEngine

from bot import crud, models, schemas


class TelegramService:
    """Методы для запросов в БД."""

    engine: AsyncEngine

    async def add_chat(self, **values) -> models.Channel:
        """Добавление ТГ канала."""
        async with self.engine.begin() as conn:
            return await crud.ChannelRepository(conn).add(**values)

    async def show_chats(self) -> Sequence[models.Channel]:
        """Список доступных ТГ каналов."""
        async with self.engine.begin() as conn:
            return await crud.ChannelRepository(conn).list()

    async def get_chat(self, chat_id: int) -> Any:
        """Поиск ТГ канала по id."""
        async with self.engine.begin() as conn:
            return await crud.ChannelRepository(conn).get(id=chat_id)

    async def delete_chat(self, chat_id: int) -> None:
        """Удаление ТГ канала."""
        async with self.engine.begin() as conn:
            return await crud.ChannelRepository(conn).delete(id=chat_id)

    async def show_user_filters(self, user_id: int) -> Sequence[Any]:
        """Поиск фильтров по id пользователя."""
        async with self.engine.begin() as conn:
            return await crud.SearchItemRepository(conn).list(models.SearchItem.user_id == user_id)

    async def get_searchitems(
        self,
        grades: list[schemas.Grades],
        languages: list[schemas.Languages],
    ) -> Sequence[models.SearchItem]:
        """Поиск пользовательских фильтров с заданными настройками."""
        async with self.engine.begin() as conn:
            return await crud.SearchItemRepository(conn).list(
                models.SearchItem.language.in_(languages),
                models.SearchItem.grade.in_(grades),
            )

    async def create_searchitem(self, user_id: int, grade: str, language: str) -> models.SearchItem:
        """Создание пользовательского фильтра."""
        async with self.engine.begin() as conn:
            await crud.UserRepository(conn).get_or_create(id=user_id)
            return await crud.SearchItemRepository(conn).get_or_create(
                user_id=user_id,
                grade=grade.casefold(),
                language=language.casefold(),
            )

    async def delete_searchitem(self, searchitem_id: int) -> None:
        async with self.engine.begin() as conn:
            await crud.SearchItemRepository(conn).delete(id=searchitem_id)

    async def get_user(self, user_id: int) -> Any:
        async with self.engine.begin() as conn:
            return await crud.UserRepository(conn).get(id=user_id)

    async def delete_user(self, user_id: int) -> None:
        async with self.engine.begin() as conn:
            await crud.UserRepository(conn).delete(id=user_id)
