# Импорт класса для тестирования
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

#
def test_checkstatus():
    response = client.get("/api/v1/")
    assert response.status_code == 200