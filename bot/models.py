"""Модели БД."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression, func
from sqlalchemy_utils import ChoiceType

from bot import schemas

Base = declarative_base()


class TimeStampModel(Base):
    """Абстрактная модель со штампами времени."""

    __abstract__ = True

    created_at = sa.Column(sa.DateTime(True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(True), onupdate=datetime.utcnow, server_default=func.now())

    def __str__(self):
        return f'{self.__class__.__name__} id={self.id}'


class User(TimeStampModel):
    """Модель пользователя."""

    __tablename__ = 'users'

    id = sa.Column(sa.BigInteger, primary_key=True, index=True, unique=True)
    is_superuser = sa.Column(sa.Boolean, server_default=expression.false())
    no_grade_ok = sa.Column(sa.Boolean, server_default=expression.false())  # выпилить
    grade = sa.Column(sa.String)  # выпилить


class SearchItem(TimeStampModel):
    __tablename__ = 'searchitems'

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    grade = sa.Column(ChoiceType(schemas.Grades), nullable=False)
    language = sa.Column(ChoiceType(schemas.Languages), nullable=False)


class Channel(TimeStampModel):
    """Модель Телеграм-канала."""

    __tablename__ = 'channels'
    __table_args__ = (sa.PrimaryKeyConstraint('id', 'language'),)

    id = sa.Column(sa.BigInteger, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    language = sa.Column(ChoiceType(schemas.Languages), nullable=False)
