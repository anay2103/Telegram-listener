"""Cхемы."""
from enum import Enum

from pydantic import BaseModel, constr


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


class Keyword(BaseModel):
    """Схема ключевого слова."""

    name: constr(max_length=256)
    mode: KeywordModes

    def __str__(self):
        return f'{self.name}: {self.mode}'
