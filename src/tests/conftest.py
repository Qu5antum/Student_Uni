from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import FastAPI
import pytest, asyncio, pytest_asyncio
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
@pytest_asyncio.fixture(scope='session')
async def async_db_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope='function')
async def async_db(async_db_engine):
    async with TestingSessionLocal() as session:

        yield session

        await session.close()


@pytest.fixture(scope="session")
def app_fixture():
    return app


@pytest_asyncio.fixture
async def async_client(app_fixture, async_db):

    app_fixture.dependency_overrides = {}

    async def override_get_db():
        yield async_db

    app_fixture.dependency_overrides[get_session] = override_get_db

    transport = ASGITransport(app=app_fixture)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client

    app_fixture.dependency_overrides.clear()



