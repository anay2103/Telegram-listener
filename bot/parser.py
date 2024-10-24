import re
from typing import Optional, Set

from bot import schemas, models
from bot.crud import UserRepository


class Parser:
    """Парсер сообщений."""

    recipients: Set
    user_repository: UserRepository

    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    any_grade = r'lead[^\w]|senior|middle|jun(ior)?|intern[^\w]|architect[^\w]|Архитектор|Тимлид'
    no_teamlead = '^((?![Ll]ead).)*$'
    python_developer = (
        r'python.*(developer|разработчик\W|программист\W|вакансия\W|backend|engineer)|'
        r'(developer|разработчик\W|программист\W|вакансия\W|backend|engineer).*python'
    )
    junior = r'[Ii]ntern[^\w]|[Jj]un(?:ior)'
    middle = '[Mm]iddle'
    senior = '[Ss]enior'
    stop_words = '[Рр]еклама'
    heading = r'((?:[^\n]+\n?\n?){1,2})'
    cv = r'резюме|cv|[^\w][яiI]\s'

    async def check_stop_words(self, text: str) -> bool:
        """Проверка на рекламные сообщения."""
        stop_words = re.search(self.stop_words, text)
        return bool(stop_words)

    async def check_cv(self, text: str) -> bool:
        """Проверка что в сообщении резюме, а не вакансия."""
        if heading := re.search(self.heading, text):
            return bool(re.search(self.cv, heading[0], re.IGNORECASE))
        return False

    async def remove_urls(self, text: str) -> str:
        """Очистка проверяемого текста от url-адресов."""
        return re.sub(self.url_regex, '', text)

    async def check_python_developer(self, text: str) -> Optional[re.Match[str]]:
        """Проверка на название вакансии."""
        return re.search(self.python_developer, text, re.DOTALL | re.IGNORECASE)

    async def check_any_grade(self, text: str, recipients: Set[models.User]) -> Set[models.User]:
        """Проверка на отсутствие грейда в вакансии."""
        if not re.search(self.any_grade, text, re.IGNORECASE):
            recipients.update(await self.user_repository.list(no_grade_ok=True))
        return recipients

    async def check_junior(self, text: str, recipients: Set[models.User]) -> Set[models.User]:
        """Проверка на грейд junior."""
        if bool(re.search(self.junior, text)):
            recipients.update(await self.user_repository.list(grade=schemas.Grades.JUNIOR.name))
        return recipients

    async def check_middle(self, text: str, recipients: Set[models.User]) -> Set[models.User]:
        """Проверка на грейд middle."""
        if bool(re.search(self.middle, text)):
            recipients.update(await self.user_repository.list(grade=schemas.Grades.MIDDLE.name))
        return recipients

    async def check_senior(self, text: str, recipients: Set[models.User]) -> Set[models.User]:
        """Проверка на грейд senior."""
        if bool(re.search(self.senior, text)):
            recipients.update(await self.user_repository.list(grade=schemas.Grades.SENIOR.name))
        return recipients

    async def process(self, text: str) -> Set[models.User]:
        """Проверка текста сообщения.

        При наличии выбранного грейда в тексте пользователь включается в список получателей.
        """
        recipients: Set[models.User] = set()
        if (await self.check_stop_words(text)):
            return recipients

        if (await self.check_cv(text)):
            return recipients

        text = await self.remove_urls(text)

        if (await self.check_python_developer(text)):
            recipients = await self.check_any_grade(text, recipients)
            recipients = await self.check_junior(text, recipients)
            recipients = await self.check_middle(text, recipients)
            recipients = await self.check_senior(text, recipients)
        return recipients
