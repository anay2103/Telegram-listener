from enum import StrEnum


class Grades (StrEnum):
    """Грейды вакансий."""

    JUNIOR = 'junior'
    MIDDLE = 'middle'
    SENIOR = 'senior'
    LEAD = 'techlead'


class Languages(StrEnum):
    """Язык программирования."""

    GO = 'go'
    PYTHON = 'python'


class UserState(StrEnum):
    """Статусы пользователя."""

    choosing_language = 'choosing language'
    сhoosing_grade = 'choosing grade'
    deleting_filter = 'deleting filter'
    deleting_me = 'deleting me'


class ChannelAdminState(StrEnum):
    """Статусы админа при работе с чатами."""

    adding_channel = 'adding_channel'
    deleting_channel = 'deleting_channel'
