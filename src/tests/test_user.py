import pytest
import pytest_asyncio
from sqlalchemy import select

from src.app.database.models import Role


@pytest_asyncio.fixture
async def admin_client(async_client, session):


    role = await session.scalar(
        select(Role).where(Role.name == "ADMIN")
    )

    register_response = await async_client.post(
        "/user/register_personel",
        json={
            "email": "admin@mail.com",
            "password": "Password123_",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code in (201)

    login_response = await async_client.post(
        "/user/login",
        data={
            "username": "admin@mail.com",
            "password": "Password123_"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    async_client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return async_client

@pytest.mark.asyncio
async def test_admin_can_create_student(admin_client, faculty, section):

    response = await admin_client.post(
        "/user/register_student",
        json={
            "student_id": 1,
            "name": "Ali",
            "surname": "Veli",
            "class_": "1",
            "password": "Password123_",
            "faculty_id": faculty["id"],
            "section_id": section["id"]
        }
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_protected_without_token(async_client):

    response = await async_client.get("/procted")

    assert response.status_code == 401


