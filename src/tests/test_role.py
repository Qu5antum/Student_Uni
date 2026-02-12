import pytest_asyncio
from src.app.database.models import Role

@pytest_asyncio.fixture(scope="session", autouse=True)
async def seed_roles(async_db):

    admin_role = Role(name="ADMIN")
    student_role = Role(name="STUDENT")

    async_db.add_all([admin_role, student_role])
    await async_db.commit()