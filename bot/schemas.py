from enum import StrEnum


class Grades(StrEnum):
    """Грейды вакансий."""

    JUNIOR = 'junior'
    MIDDLE = 'middle'
    SENIOR = 'senior'
    LEAD = 'techlead'


class Languages(StrEnum):
    """Язык программирования."""

    GOLANG = 'golang'
    PYTHON = 'python'
