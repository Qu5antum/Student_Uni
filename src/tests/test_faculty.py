import pytest_asyncio

@pytest_asyncio.fixture
async def test_faculty(async_client):

    response = await async_client.post(
        "/faculty/new_faculty",
        json={
            "name": "Engineering"
        }
    )

    assert response.status_code == 201

    return response.json()
