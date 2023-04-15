"""Операции в БД."""
from typing import Any, List, Optional

from sqlalchemy.sql.expression import delete, insert, select, update
from sqlalchemy.orm import sessionmaker

from bot import models, schemas


class Repository:
    """Базовый класс для операций в БД."""

    def __init__(self, session: sessionmaker) -> None:
        self.session = session


class UserRepository(Repository):
    """Репозиторий модели пользователя."""

    async def add(self, **values: Any) -> models.User:
        """Добавление пользователя."""
        async with self.session.begin() as session:
            query = insert(models.User).values(**values)
            user = await session.execute(query)
        return user

    async def update(self, id: int, **values) -> None:
        """Обновление пользователя."""
        async with self.session.begin() as session:
            query = update(models.User)
            query = query.filter_by(id=id)
            query = query.values(**values)
            await session.execute(query)

    async def get(self, id: int) -> models.User:
        """Получение пользователя по id."""
        async with self.session.begin() as session:
            query = select(models.User).filter_by(id=id)
            res = await session.execute(query)
        return res.scalar()

    async def list(self) -> List[models.User]:
        """Список пользователей с их ключевыми словами."""
        async with self.session.begin() as session:
            query = select(models.User)
            users = await session.execute(query)
        return users.scalars().all()

    async def apply_query(self, text: str):
        """Список пользователей, запрос которых найден найден в строке текста."""
        users = await self.list()
        async with self.session.begin() as session:
            for user in users:
                query = "SELECT to_tsvector(translate(%s, %s, %s)) @@ to_tsquery(%s)" % (
                    f"'{text}'", "'/'", "' '", user.query
                )
                if (await session.execute(query)).scalar():
                    yield user

    async def make_query(self, user_id: int) -> None:
        """Построение строки запроса пользователя и обновление."""
        keywords = await KeywordRepository(self.session).get(user_id)
        query = await self._make_query(keywords)
        await UserRepository(self.session).update(user_id, query=query)

    @staticmethod
    async def _make_query(keywords: List[models.Keyword]) -> str:
        """Построение строки запроса из ключевых слов."""
        query = ''
        for kw in keywords:
            token = f"''{kw.name}''"  # кавычки используются Postgres для поиска фразы
            if kw.mode == schemas.KeywordModes.binding:
                query = f'{token} & {query}' if query else f'{token}'
            elif kw.mode == schemas.KeywordModes.negative:
                query = f'!{token} & {query}' if query else f'!{token}'

        qr_opt = ''
        for kw in keywords:
            token = f"''{kw.name}''"  # кавычки используются Postgres для поиска фразы
            if kw.mode == schemas.KeywordModes.optional:
                qr_opt = f'{token} & {query} | {qr_opt}' if query else f'{token} | {qr_opt}'

        return f"'{qr_opt.rstrip(' | ')}'" if qr_opt else f"'{query}'"


class KeywordRepository(Repository):
    """Репозиторий модели ключевого слова."""

    async def add(self, keyword: str, mode: str, user_id: int) -> None:
        """Добавление ключевого слова для пользователя.

        Если пользователь новый, сначала добавляем пользователя.
        """
        user = await UserRepository(self.session).get(id=user_id)
        if not user:
            user = await UserRepository(self.session).add(id=user_id)

        async with self.session.begin() as session:
            query = insert(models.Keyword)
            query = query.values(name=keyword, mode=mode, user_id=user_id)
            await session.execute(query)

    async def get(self, user_id: Optional[int] = None) -> List[models.Keyword]:
        """Получение ключевых слов по id пользователя."""
        async with self.session.begin() as session:
            query = select(models.Keyword).filter_by(user_id=user_id)
            res = await session.execute(query)
        return res.scalars().all()

    async def delete(self, name: str, user_id: int) -> None:
        """Удаление ключевых слов пользователя."""
        async with self.session.begin() as session:
            query = delete(models.Keyword)
            query = query.filter_by(name=name, user_id=user_id)
            await session.execute(query)


class ChannelRepository(Repository):
    """Репозиторий модели чата."""

    async def add(self, **values: Any) -> None:
        """Добавление чата."""
        async with self.session.begin() as session:
            query = insert(models.Channel).values(**values)
            await session.execute(query)

    async def get(self, id: int) -> models.Channel:
        """Получение чата по id."""
        async with self.session.begin() as session:
            query = select(models.Channel).filter_by(id=id)
            res = await session.execute(query)
        return res.scalar()

    async def list(self) -> List[models.Channel]:
        """Список чатов."""
        async with self.session.begin() as session:
            query = select(models.Channel)
            users = await session.execute(query)
        return users.scalars().all()

    async def delete(self, id: int) -> None:
        """Удаление чата."""
        async with self.session.begin() as session:
            query = delete(models.Channel)
            query = query.filter_by(id=id)
            await session.execute(query)
