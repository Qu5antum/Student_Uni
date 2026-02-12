import pytest_asyncio
from src.app.database.models import Role
from .conftest import TestingSessionLocal

@pytest_asyncio.fixture(scope="session", autouse=True)
async def seed_roles(async_db_engine):

    async with TestingSessionLocal() as session:
        session.add_all([
            Role(name="ADMIN"),
            Role(name="STUDENT"),
        ])
        await session.commit()