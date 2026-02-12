import pytest_asyncio

@pytest_asyncio.fixture
async def test_section(async_client, faculty):

    response = await async_client.post(
        "/section/new_section",
        json={
            "name": "Computer Science",
            "faculty_id": faculty["id"]
        }
    )

    assert response.status_code == 201

    return response.json()
