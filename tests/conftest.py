import asyncio
import os

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Any, AsyncGenerator, Callable, Generator, Optional

from bot.models import Base
from bot import client,  crud, models, schemas, settings


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def database_url() -> Optional[str]:
    """Database URI."""
    os.environ['POSTGRES_DB'] = 'pytest'
    return settings.build_postgres_uri()


@pytest.fixture(scope='session')
def init_database() -> Callable[[Any], None]:
    """Database factory."""
    return Base.metadata.create_all


@pytest.fixture
async def tgclient(sqla_engine) -> client.Client:
    """Telegram client."""
    app = client.Client(session=None, api_id=settings.API_ID, api_hash=settings.API_HASH)
    session = sessionmaker(sqla_engine,  expire_on_commit=False, class_=AsyncSession)
    app.user_repository = crud.UserRepository(session)
    app.channel_repository = crud.ChannelRepository(session)
    return app


@pytest.fixture
async def make_user(sqla_engine) -> AsyncGenerator:
    """User instance."""
    db_session = sessionmaker(sqla_engine,  expire_on_commit=False, class_=AsyncSession)

    async def make(
        grade: str = schemas.Grades.JUNIOR.name,
        no_grade_ok: bool = False,
    ) -> models.User:
        query = sa.insert(models.User)
        query = query.values(grade=grade, no_grade_ok=no_grade_ok)
        async with db_session.begin() as session:
            result = await session.execute(query.returning(models.User))
            user, *_ = result.one()
            return user
    yield make

    async with db_session.begin() as session:
        await session.execute(sa.delete(models.User))
