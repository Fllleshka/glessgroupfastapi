import pytest
from fastapi.testclient import TestClient

from main import mainapp


@pytest.fixture(scope="session")
def app():
    return mainapp()


@pytest.fixture(scope="session")
def client(app):
    with TestClient(app) as c:   # with ← запускает lifespan
        yield c