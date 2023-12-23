import re
from typing import Optional, Set

from bot import schemas
from bot.crud import UserRepository


class Parser:
    """Парсер сообщений."""

    recipients: Set
    user_repository: UserRepository

    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    any_grade = r'[Tt]e[am|ch]+\W*[Ll]ead|[Ss]enior|[Mm]iddle|[Jj]un(ior)?'
    no_teamlead = r'^((?![Tt]e[am|ch]+\W*[Ll]ead).)*$'
    python_developer = (
        '[Pp]ython.*([Dd]eveloper|[Рр]азработчик|[Пр]ограммист|[Bb]ackend|[Ee]ngineer)|'
        '([Dd]eveloper|[Рр]азработчик|[Пр]ограммист|[Bb]ackend|[Ee]ngineer).*[Pp]ython'
    )
    no_middle = '^(?![Mm]iddle).*$'
    no_senior = '^((?![Ss]enior).)*$'
    junior = '[Jj]un(?:ior)'
    middle = '[Mm]iddle'
    senior = '[Ss]enior'
    stop_words = '[Рр]еклама'
    utm_marker = 'utm'  # utm-разметка ссылок

    async def check_stop_words(self, text: str) -> bool:
        """Проверка на рекламные сообщения."""
        urls = re.findall(self.url_regex, text)
        utms = any([re.search(self.utm_marker, url) for url in urls])
        stop_words = re.search(self.stop_words, text)
        return bool(utms or stop_words)

    async def check_python_developer(self, text: str) -> Optional[re.Match[str]]:
        """Проверка на название вакансии."""
        return re.search(self.python_developer, text, re.DOTALL)

    async def check_any_grade(self, text: str) -> None:
        """Проверка на отсутствие грейда в вакансии."""
        if not re.search(self.any_grade, text):
            self.recipients.update(await self.user_repository.list(no_grade_ok=True))

    async def check_junior(self, text: str) -> None:
        """Проверка на грейд junior."""
        if bool(re.search(self.junior, text) and re.search(self.no_middle, text, re.DOTALL)):
            self.recipients.update(await self.user_repository.list(grade=schemas.Grades.JUNIOR.name))

    async def check_middle(self, text: str) -> None:
        """Проверка на грейд middle."""
        if bool(re.search(self.middle, text) and re.search(self.no_senior, text, re.DOTALL)):
            self.recipients.update(await self.user_repository.list(grade=schemas.Grades.MIDDLE.name))

    async def check_senior(self, text: str) -> None:
        """Проверка на грейд senior."""
        if bool(re.search(self.senior, text) and re.search(self.no_teamlead, text, re.DOTALL)):
            self.recipients.update(await self.user_repository.list(grade=schemas.Grades.SENIOR.name))

    async def process(self, text: str) -> None:
        """Проверка текста сообщения.

        При наличии выбранного грейда в тексте пользователь включается в список получателей.
        """
        self.recipients.clear()
        if (await self.check_stop_words(text)):
            return

        if (await self.check_python_developer(text)):
            await self.check_any_grade(text)
            await self.check_junior(text)
            await self.check_middle(text)
            await self.check_senior(text)
