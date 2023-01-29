from typing import TYPE_CHECKING, AsyncGenerator, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func

if TYPE_CHECKING:
    import bot.models as models


class MessageParser:
    """Обработчик сообщений Телеграма."""

    def __init__(self, session: AsyncSession, text: str) -> None:
        self.session = session
        self.text = text

    async def get_ts_rank(self, users: List['models.User']) -> AsyncGenerator:
        """Поиск по ключевым словам каждого пользователя.

        Сейчас слова соединяются оператором OR. Подумать, как реализовать отрицание.
        """
        async with self.session.begin():
            for user in users:
                keyword_str = ' | '.join([keyword.name for keyword in user.keywords])
                ts_query = func.to_tsquery(keyword_str)
                rank = await self.session.execute(func.ts_rank(func.to_tsvector(self.text), ts_query))
                yield user, rank.scalar()
