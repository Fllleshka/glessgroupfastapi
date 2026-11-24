"""Тесты ручек call-центра: включение (/inclusion) и выключение (/shutdown) менеджера.

Ручка проверяется целиком через TestClient, но две её зависимости подменяются:
- база данных: вместо файла users.sqlite3 — SQLite в памяти с одним менеджером;
- сервис Beeline: вместо настоящих запросов — функция-заглушка.
Так тесты не трогают рабочую базу, не ходят в интернет и не требуют токена.
"""
import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database.engine import UsersBase, get_users_session
from database.models import Users
from routers import callcenter

# Короткий номер менеджера, который есть в тестовой базе
MANAGER_NUMBER = 105
# Номер, которого в тестовой базе нет
UNKNOWN_NUMBER = 999

# Обе ручки устроены одинаково, поэтому большинство тестов прогоняется для каждой:
# адрес ручки и статус, который она должна передать в Beeline
ENDPOINTS = [
    ("/api/v1/inclusion", "ONLINE"),
    ("/api/v1/shutdown", "OFFLINE"),
]


# Тестовая база: SQLite в памяти с одним менеджером.
# Подменяем ею зависимость get_users_session, а после теста возвращаем всё как было.
@pytest.fixture
def test_db(app):
    # StaticPool — одно соединение на всех. Без него ручка, которая выполняется
    # в другом потоке, получила бы новую пустую базу без таблиц.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    UsersBase.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Users(
            key="MANAGER",
            firstname="Иван",
            secondname="Иванов",
            patronymic="Иванович",
            shortname="Иванов И.И.",
            fullname="Иванов Иван Иванович",
            shortnumber=MANAGER_NUMBER,
        ))
        session.commit()

    def override_get_users_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_users_session] = override_get_users_session
    yield
    # Убираем подмену: фикстура app живёт весь прогон, подмена не должна попасть в другие тесты
    app.dependency_overrides.pop(get_users_session, None)
    engine.dispose()


# Заглушка Beeline: ничего никуда не отправляет, запоминает вызовы
# и возвращает тот статус, который у неё попросили.
# Подменяем в модуле routers.callcenter — там, где функция используется.
@pytest.fixture
def beeline_calls(monkeypatch):
    calls = []

    def fake_set_agent_status(shortnumber, status):
        calls.append((shortnumber, status))
        return status

    monkeypatch.setattr(callcenter, "set_agent_status", fake_set_agent_status)
    return calls


# Менеджер есть в базе, Beeline ответил: 200 и статус в ответе
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_change_status_success(client, test_db, beeline_calls, url, status):
    response = client.get(f"{url}/{MANAGER_NUMBER}")

    assert response.status_code == 200
    assert response.json() == {"result": True, "status": status, "comment": "Выполнено"}
    # Beeline вызван ровно один раз, с нужным номером и статусом
    assert beeline_calls == [(MANAGER_NUMBER, status)]


# Номера нет в базе: 404, и в Beeline ничего не отправляется
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_unknown_number_returns_404(client, test_db, beeline_calls, url, status):
    response = client.get(f"{url}/{UNKNOWN_NUMBER}")

    assert response.status_code == 404
    assert beeline_calls == []


# Beeline недоступен или ответил ошибкой: 502, а подробности ошибки клиенту не уходят
@pytest.mark.parametrize("error", [requests.ConnectionError, requests.Timeout, requests.HTTPError])
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_beeline_error_returns_502(client, test_db, monkeypatch, url, status, error):
    def broken_set_agent_status(shortnumber, status):
        raise error("внутренняя подробность ошибки")

    monkeypatch.setattr(callcenter, "set_agent_status", broken_set_agent_status)

    response = client.get(f"{url}/{MANAGER_NUMBER}")

    assert response.status_code == 502
    assert "внутренняя подробность ошибки" not in response.text


# Вместо номера — текст: FastAPI отвечает 422 ещё до входа в ручку
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_not_a_number_returns_422(client, test_db, beeline_calls, url, status):
    response = client.get(f"{url}/abc")

    assert response.status_code == 422
    assert beeline_calls == []


# Ручки принимают только GET
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_wrong_method_returns_405(client, url, status):
    response = client.post(f"{url}/{MANAGER_NUMBER}")

    assert response.status_code == 405
