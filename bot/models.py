"""Модели БД."""
from uuid import uuid4
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression, func

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
    no_grade_ok = sa.Column(sa.Boolean, server_default=expression.false())
    grade = sa.Column(sa.String)
    # TODO: выпилить
    query = sa.Column(sa.String)


# TODO: выпилить
class Keyword(TimeStampModel):
    """Модель ключевого слова."""
    __tablename__ = 'keywords'

    id = sa.Column(pg.UUID, index=True, unique=True, default=lambda: str(uuid4()))
    mode = sa.Column(sa.Enum(schemas.KeywordModes), nullable=False, default=schemas.KeywordModes.optional)
    name = sa.Column(sa.String, primary_key=True)
    user_id = sa.Column(sa.ForeignKey('users.id'), primary_key=True)


class Channel(TimeStampModel):
    """Модель Телеграм-канала."""
    __tablename__ = 'channels'

    id = sa.Column(sa.BigInteger, primary_key=True, index=True, unique=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
