from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import FastAPI
import pytest, asyncio, pytest_asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from src.app.core.config import settings
from src.app.database.db import Base, get_session
from src.app.main import app
from src.app.database.models import Role


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

        await session.rollback()


@pytest.fixture(scope="session")
def app_fixture():
    return app


@pytest_asyncio.fixture
async def async_client(app_fixture, async_db):

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


@pytest_asyncio.fixture
async def faculty(async_client):

    response = await async_client.post(
        "/faculty/new_faculty",
        json={
            "name": "Engineering"
        }
    )

    assert response.status_code == 201

    return response.json()


@pytest_asyncio.fixture
async def section(async_client, faculty):

    response = await async_client.post(
        "/section/new_section",
        json={
            "name": "Computer Science",
            "faculty_id": faculty["id"]
        }
    )

    assert response.status_code == 201

    return response.json()


@pytest_asyncio.fixture
async def test_course(async_client, section):

    response = await async_client.post(
        "/course/new_course",
        json={
            "name": "Algorithms",
            "section_id": section["id"]
        }
    )

    assert response.status_code == 201

    return response.json()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def seed_roles(async_db_engine):

    async with async_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        result = await session.execute(select(Role))
        if result.scalars().first():
            return

        session.add_all([
            Role(name="ADMIN"),
            Role(name="STUDENT"),
        ])
        await session.commit()


