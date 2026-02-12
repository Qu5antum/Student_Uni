import pytest_asyncio

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
