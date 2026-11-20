import pytest
from fastapi.testclient import TestClient

from main import mainapp

collect_ignore = ["test_callcenter.py"]

@pytest.fixture(scope="session")
def app():
    return mainapp()


@pytest.fixture(scope="session")
def client(app):
    with TestClient(app) as c:   # with ← запускает lifespan
        yield c