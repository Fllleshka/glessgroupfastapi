import pytest

from routers import checkstatus

URL = "/api/v1/"
HEALTH_URL = "/api/v1/health"


# Проверяем, что сервис отвечает
def test_check_status_success(client):
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() is True


# Проверяем, что ручка принимает только GET
@pytest.mark.parametrize("method", ["post", "put", "delete"])
def test_check_status_wrong_method(client, method):
    response = getattr(client, method)(URL)

    assert response.status_code == 405


# Проверяем, что /health отвечает "ok", когда обе базы доступны
def test_health_success(client):
    response = client.get(HEALTH_URL)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["databases"] == {"users": "ok", "products": "ok"}
    assert body["version"] == client.app.version


# Проверяем, что /health отдаёт 503, если одна из баз недоступна
@pytest.mark.parametrize("broken", ["users", "products"])
def test_health_broken_database(client, monkeypatch, broken):
    real_check = checkstatus.check_database

    # Подменяем проверку: выбранная база «сломана», вторая проверяется по-настоящему
    def fake_check(engine, table):
        if table == broken:
            return "OperationalError: no such table"
        return real_check(engine, table)

    monkeypatch.setattr(checkstatus, "check_database", fake_check)

    response = client.get(HEALTH_URL)

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "error"
    assert body["databases"][broken] == "error"
    # Текст ошибки наружу не отдаётся
    assert "OperationalError" not in response.text