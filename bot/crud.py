"""Операции в БД."""

from typing import Any, Optional, Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from bot import models


class Repository:
    """Базовый класс для операций в БД."""

    table: sa.TableClause

    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def add(self, **values: Any) -> Any:
        query = sa.insert(self.table)
        query = query.values(**values).returning(self.table)
        res = await self.conn.execute(query)
        return res.scalar()

    async def update(self, id: int, **values) -> Any:
        query = sa.update(self.table)
        query = query.filter_by(id=id)
        query = query.values(**values).returning(self.table)
        res = await self.conn.execute(query)
        return res.scalar_one_or_none()

    async def update_or_create(self, id: int, **values) -> Any:
        if item := await self.update(id=id, **values):
            return item
        return await self.add(id=id, **values)

    async def get(self, id: int) -> Optional[Any]:
        query = sa.select(self.table).filter_by(id=id)
        res = await self.conn.execute(query)
        return res.one_or_none()

    async def list(self, *whereclauses) -> Sequence[Any]:
        """Получение списка объектов."""
        query = sa.select(self.table)
        query = query.where(*whereclauses)
        items = await self.conn.execute(query)
        return items.all()

    async def delete(self, id: int) -> None:
        """Удаление."""
        query = sa.delete(self.table).filter_by(id=id)
        await self.conn.execute(query)


class UserRepository(Repository):
    """Репозиторий модели пользователя."""

    table = models.User.__table__


class ChannelRepository(Repository):
    """Репозиторий модели чата."""

    table = models.Channel.__table__


class SearchItemRepository(Repository):
    """Репозиторий модели фильтра поиска."""

    table = models.SearchItem.__table__
