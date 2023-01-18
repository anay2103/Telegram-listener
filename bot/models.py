from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import expression, func

Base = declarative_base()


class TimeStampModel(Base):
    __abstract__ = True

    created_at = sa.Column(sa.DateTime(True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(True), onupdate=datetime.utcnow, server_default=func.now())

    def __str__(self):
        return f'{self.__class__.__name__} id={self.id}'


user_keywords = sa.Table(
    'user_keywords',
    Base.metadata,
    sa.Column('user_id', sa.ForeignKey('users.id'), primary_key=True),
    sa.Column('keyword_id', sa.ForeignKey('keywords.id'), primary_key=True)
)


class User(TimeStampModel):
    __tablename__ = 'users'

    id = sa.Column(sa.BigInteger, primary_key=True, index=True, unique=True)
    is_superuser = sa.Column(sa.Boolean, server_default=expression.false())
    keywords = relationship('Keyword', secondary=user_keywords, back_populates='user')


class Keyword(TimeStampModel):
    __tablename__ = 'keywords'

    id = sa.Column(sa.Integer, primary_key=True, index=True, unique=True)
    name = sa.Column(sa.String, nullable=False)
    user = relationship('User', secondary=user_keywords, back_populates='keywords')


class Channel(TimeStampModel):
    __tablename__ = 'channels'

    id = sa.Column(sa.Integer, primary_key=True, index=True, unique=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
