from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import bot.models as models


class StoreException(Exception):
    """Ошибка операции в БД."""


class Repository:
    """Базовый класс репозитория для операций в БД."""

    def __init__(self, session):
        self.session = session


class UserRepository(Repository):
    """Репозиторий модели пользователя."""

    async def add(self, id: int) -> None:
        async with self.session.begin():
            user = models.User(id=id)
            await self.session.add(user)

    async def get(self, id: int) -> models.User:
        async with self.session.begin():
            query = select(models.User).where(models.User.id == id).options(selectinload(models.User.keywords))
            user = await self.session.execute(query)
            return user.scalar()

    async def list(self) -> List[models.User]:
        """Список пользователей с их ключевыми словами."""
        async with self.session.begin():
            query = select(models.User).options(selectinload(models.User.keywords))
            user_qs = await self.session.execute(query)
            return user_qs.scalars().all()


class ChannelRepository(Repository):
    """Репозиторий модели чата."""

    async def add(self, id: int, name: str) -> None:
        async with self.session.begin():
            channel = models.Channel(id=id, name=name)
            self.session.add(channel)

    async def get(self, id: int) -> models.Channel:
        async with self.session.begin():
            channel_qs = await self.session.execute(select(models.Channel).where(models.Channel.id == id))
            return channel_qs.scalar()

    async def list(self) -> List[models.Channel]:
        async with self.session.begin():
            channel_qs = await self.session.execute(select(models.Channel))
            return channel_qs.scalars().all()


class KeywordRepository(Repository):
    """Репозиторий модели ключевого слова."""

    async def add(self, keywords, sender) -> None:
        user = await UserRepository(self.session).get(id=sender.id)
        async with self.session.begin():
            if not user:
                user = models.User(id=sender.id)
                self.session.add(user)
            for keyword in keywords:
                user.keywords.append(models.Keyword(name=keyword))

    async def delete(self, keywords, sender) -> None:
        # TODO: проверить есть ли менее корявое удаление
        user = await UserRepository(self.session).get(id=sender.id)
        if not user:
            raise StoreException((f'Пользователь не найден id={sender.id}'))
        async with self.session.begin():
            for keyword in keywords:
                try:
                    query = select(models.Keyword).join(
                        models.Keyword.user).where(
                        models.User.id == sender.id).where(
                        models.Keyword.name == keyword)
                    keyword_qs = await self.session.execute(query)
                    user.keywords.remove(keyword_qs.scalar())
                except ValueError:
                    raise StoreException(f'ключевое слово не найдено {keyword}')
