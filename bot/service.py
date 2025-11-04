from typing import Any, Sequence, Type

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy_file import File

from bot import crud, models, schemas


class BaseTelegramService:
    repository: Type[crud.Repository]

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession], **kwargs):
        self.sessionmaker = sessionmaker

    async def add_item(self, **values: dict[str, Any]) -> None:
        async with self.sessionmaker.begin() as session:
            return await self.repository(session).add(**values)

    async def update_item(self, _id: int, **values: dict[str, Any]):
        async with self.sessionmaker.begin() as session:
            return await self.repository(session).update(_id, **values)

    async def filter_item(self, **filters: list):
        async with self.sessionmaker.begin() as session:
            return await self.repository(session).filter_one(**filters)

    async def get_list(self, *filters: list):
        async with self.sessionmaker.begin() as session:
            return await self.repository(session).list(*filters)

    async def delete_item(self, _id: int):
        async with self.sessionmaker.begin() as session:
            return await self.repository(session).delete(_id)


class ChannelService(BaseTelegramService):
    """Методы для запросов в БД."""

    repository = crud.ChannelRepository


class SearchItemsService(BaseTelegramService):
    repository = crud.SearchItemRepository

    async def show_user_filters(self, user_id: int) -> Sequence[models.SearchItem]:
        """Поиск фильтров по id пользователя."""
        return await self.get_list(models.SearchItem.user_id == user_id)

    async def get_searchitems(
        self,
        grades: list[schemas.Grades],
        languages: list[schemas.Languages],
    ) -> Sequence[models.SearchItem]:
        """Поиск пользовательских фильтров с заданными настройками."""
        return await self.get_list(
            models.SearchItem.language.in_(languages),
            models.SearchItem.grade.in_(grades),
        )

    async def create_searchitem(self, user_id: int, grade: str, language: str) -> models.SearchItem:
        """Создание пользовательского фильтра."""
        async with self.sessionmaker.begin() as session:
            await crud.UserRepository(session).get_or_create(id=user_id)
            return await self.repository(session).get_or_create(
                user_id=user_id,
                grade=grade.casefold(),
                language=language.casefold(),
            )


class UserService(BaseTelegramService):
    repository = crud.UserRepository


class CVService(BaseTelegramService):
    repository = crud.CVRepository

    async def add_item(self, user_id: int, content: bytes, filename: str, content_type: str) -> None:
        file = File(content=content, filename=filename, content_type=content_type)
        async with self.sessionmaker.begin() as session:
            return await self.repository(session).add(user_id=user_id, content=file, name=filename)

    async def show_user_resumes(self, user_id: int) -> Sequence[models.SearchItem]:
        return await self.get_list(models.CV.user_id == user_id)
