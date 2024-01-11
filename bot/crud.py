"""Операции в БД."""
from typing import Any, List

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from bot import models


class Repository:
    """Базовый класс для операций в БД."""

    def __init__(self, session: sessionmaker) -> None:
        self.session = session


class UserRepository(Repository):
    """Репозиторий модели пользователя."""

    async def add(self, **values: Any) -> models.User:
        """Добавление пользователя."""
        async with self.session.begin() as session:
            query = sa.insert(models.User).values(**values)
            user = await session.execute(query)
            return user

    async def update(self, id: int, **values) -> None:
        """Обновление пользователя."""
        user = await self.get(id=id)
        if not user:
            user = await self.add(id=id, **values)
            return
        async with self.session.begin() as session:
            query = sa.update(models.User)
            query = query.filter_by(id=id)
            query = query.values(**values)
            await session.execute(query)

    async def get(self, id: int) -> models.User:
        """Получение пользователя по id."""
        async with self.session.begin() as session:
            query = sa.select(models.User).filter_by(id=id)
            res = await session.execute(query)
            return res.scalar()

    async def list(self, **values) -> List[models.User]:
        """Список пользователей."""
        async with self.session.begin() as session:
            query = sa.select(models.User)
            query = query.filter_by(**values)
            users = await session.execute(query)
            return users.scalars().all()

    async def delete(self, id: int) -> None:
        """Удаление пользователя."""
        async with self.session.begin() as session:
            query = sa.delete(models.User).filter_by(id=id)
            await session.execute(query)


class ChannelRepository(Repository):
    """Репозиторий модели чата."""

    async def add(self, **values: Any) -> None:
        """Добавление чата."""
        async with self.session.begin() as session:
            query = sa.insert(models.Channel).values(**values)
            await session.execute(query)

    async def get(self, id: int) -> models.Channel:
        """Получение чата по id."""
        async with self.session.begin() as session:
            query = sa.select(models.Channel).filter_by(id=id)
            res = await session.execute(query)
            return res.scalar()

    async def list(self) -> List[models.Channel]:
        """Список чатов."""
        async with self.session.begin() as session:
            query = sa.select(models.Channel)
            users = await session.execute(query)
            return users.scalars().all()

    async def delete(self, id: int) -> None:
        """Удаление чата."""
        async with self.session.begin() as session:
            query = sa.delete(models.Channel)
            query = query.filter_by(id=id)
            await session.execute(query)
