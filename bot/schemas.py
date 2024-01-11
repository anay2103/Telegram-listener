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


class ChoosingGradeState(str, Enum):
    """Статусы пользователя."""

    сhoosing_grade = 'choosing grade'
    choosing_no_grade_ok = 'choosing no grade ok'
    deleting_grade = 'deleting grade'


class ChannelAdminState(str, Enum):
    """Статусы админа при работе с чатами."""

    adding_channel = 'adding_channel'
    deleting_channel = 'deleting_channel'
