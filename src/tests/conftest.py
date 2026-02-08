from fastapi.testclient import TestClient
from src.app import app 
import pytest

@pytest.fixture
def client():
    return TestClient(app)