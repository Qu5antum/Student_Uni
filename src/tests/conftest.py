from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import FastAPI
import pytest, asyncio
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings
from src.app.database.db import Base, get_session
from src.app.main import app

engine = create_async_engine(
    url=settings.TEST_URL_DATABASE,
    echo=True,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# drop all database every time when test complete
@pytest.fixture(scope='session')
async def async_db_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# truncate all table to isolate tests
@pytest.fixture(scope='function')
async def async_db(async_db_engine):
    async with TestingSessionLocal() as session:

        yield session

        await session.rollback()


@pytest.fixture()
async def async_client(async_db: AsyncSession):

    async def override_get_db():
        yield async_db

    app.dependency_overrides[get_session] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

# let test session to know it is running inside event loop
@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


