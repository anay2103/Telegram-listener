"""Операции в БД."""

from typing import Any, Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from bot import models


class Repository:
    """Базовый класс для операций в БД."""

    model: models.SQLModelT

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, **values: Any) -> Any:
        obj = self.model(**values)
        self.session.add(obj)

    async def update(self, id: int, **values) -> Any:
        query = sa.update(self.model)
        query = query.filter_by(id=id)
        query = query.values(**values).returning(self.model)
        res = await self.session.execute(query)
        return res.scalar_one_or_none()

    async def get_or_create(self, **filters) -> Any:
        if item := await self.filter_one(**filters):
            return item
        return await self.add(**filters)

    async def filter_one(self, **filters) -> Sequence[Any]:
        query = sa.select(self.model)
        query = query.filter_by(**filters)
        items = await self.session.scalars(query)
        return items.one_or_none()

    async def list(self, *whereclauses) -> Sequence[Any]:
        """Получение списка объектов."""
        query = sa.select(self.model)
        query = query.where(*whereclauses)
        items = await self.session.scalars(query)
        return items.all()

    async def delete(self, id: int) -> None:
        """Удаление."""
        query = sa.delete(self.model).filter_by(id=id)
        await self.session.execute(query)


class UserRepository(Repository):
    """Репозиторий модели пользователя."""

    model = models.User


class ChannelRepository(Repository):
    """Репозиторий модели чата."""

    model = models.Channel


class SearchItemRepository(Repository):
    """Репозиторий модели фильтра поиска."""

    model = models.SearchItem


class CVRepository(Repository):
    """Репозиторий модели резюме."""

    model = models.CV
