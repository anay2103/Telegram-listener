"""Cхемы."""
from enum import Enum


class KeywordModes(str, Enum):
    """Режим ключевого слова  для создания Full-text search запроса:

    - обязательное;
    - необязательное;
    - обязательно не должно встречаться в запросе.
    """
    binding = 'and'
    optional = 'or'
    negative = 'not'

    def __str__(self) -> str:
        if self == self.binding:
            return 'обязательно'
        elif self == self.optional:
            return 'опционально'
        elif self == self.negative:
            return 'исключить'
        return self


class Grades (str, Enum):
    """Грейды вакансий."""

    JUNIOR = 'junior'
    MIDDLE = 'middle'
    SENIOR = 'senior'
    LEAD = 'techlead'

    @classmethod
    def choices(cls):
        return [item.name for item in cls]
