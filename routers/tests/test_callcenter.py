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
from datetime import date

from database.engine import UsersBase, get_users_session
from database.models import Users
from routers import callcenter

from services.schedule import (
    ScheduleNotFoundError,
    ScheduleUnavailableError,
    ScheduleOpenError,
    MonthNotFoundError,
)

# Короткий номер менеджера, который есть в тестовой базе
MANAGER_FIRST_NUMBER = 105
MANAGER_SECOND_NUMBER = 106
MANAGER_THIRD_NUMBER = 107
# Номер, которого в тестовой базе нет
UNKNOWN_NUMBER = 999

# Обе ручки устроены одинаково, поэтому большинство тестов прогоняется для каждой:
# адрес ручки и статус, который она должна передать в Beeline
ENDPOINTS = [
    ("/api/v1/inclusion", "ONLINE"),
    ("/api/v1/shutdown", "OFFLINE"),
]

# Имитация графика
FAKE_SCHEDULE = {
    "ИВАНОВ И.И.": ["9"] * 31,
    "ПЕТРОВ П.П.": ["В"] * 31,
}

# Тестовая база: SQLite в памяти с тремя менеджерами.
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
            shortnumber=MANAGER_FIRST_NUMBER,
            callcenter = True
        ))
        session.add(Users(
            key="SECOND",
            firstname="Петр",
            secondname="Петров",
            patronymic="Петрович",
            shortname="Петров П.П.",
            fullname="Петров Петр Петрович",
            shortnumber=MANAGER_SECOND_NUMBER,
            callcenter = True
        ))
        session.add(Users(
            key="OTHER",
            firstname="Сергей",
            secondname="Сергеевич",
            patronymic="Сидоров",
            shortname="Сидоров С.С.",
            fullname="Сидоров Сергей Сергеевич",
            shortnumber=MANAGER_THIRD_NUMBER,
            callcenter = False
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
    response = client.post(f"{url}/{MANAGER_FIRST_NUMBER}")

    assert response.status_code == 200
    assert response.json() == {"result": True, "status": status, "comment": "Выполнено"}
    # Beeline вызван ровно один раз, с нужным номером и статусом
    assert beeline_calls == [(MANAGER_FIRST_NUMBER, status)]


# Номера нет в базе: 404, и в Beeline ничего не отправляется
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_unknown_number_returns_404(client, test_db, beeline_calls, url, status):
    response = client.post(f"{url}/{UNKNOWN_NUMBER}")

    assert response.status_code == 404
    assert beeline_calls == []


# Beeline недоступен или ответил ошибкой: 502, а подробности ошибки клиенту не уходят
@pytest.mark.parametrize("error", [requests.ConnectionError, requests.Timeout, requests.HTTPError])
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_beeline_error_returns_502(client, test_db, monkeypatch, url, status, error):
    def broken_set_agent_status(shortnumber, status):
        raise error("внутренняя подробность ошибки")

    monkeypatch.setattr(callcenter, "set_agent_status", broken_set_agent_status)

    response = client.post(f"{url}/{MANAGER_FIRST_NUMBER}")

    assert response.status_code == 502
    assert "внутренняя подробность ошибки" not in response.text


# Вместо номера — текст: FastAPI отвечает 422 ещё до входа в ручку
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_not_a_number_returns_422(client, test_db, beeline_calls, url, status):
    response = client.post(f"{url}/abc")

    assert response.status_code == 422
    assert beeline_calls == []


# Ручки принимают только GET
@pytest.mark.parametrize("url, status", ENDPOINTS)
def test_wrong_method_returns_405(client, url, status):
    response = client.get(f"{url}/{MANAGER_FIRST_NUMBER}")

    assert response.status_code == 405

# Тест активации менеджеров
def test_activate_managers(client, test_db, beeline_calls, monkeypatch):
    monkeypatch.setattr(callcenter, "load_month_schedule", lambda year, month: FAKE_SCHEDULE)

    response = client.post("/api/v1/activatemanagersonday")

    assert response.status_code == 200
    body = response.json()
    assert sorted(beeline_calls) == [(105, "ONLINE"), (106, "OFFLINE")]
    assert body["not_in_schedule"] == []

# Тест активации менеджеров человека нет в графике
def test_activate_managers_not_in_schedule(client, test_db, beeline_calls, monkeypatch):
    monkeypatch.setattr(callcenter, "load_month_schedule", lambda year, month: {"ИВАНОВ И.И.": ["9"] * 31})

    response = client.post("/api/v1/activatemanagersonday")

    assert response.status_code == 200
    body = response.json()
    assert sorted(beeline_calls) == [(105, "ONLINE")]
    assert body["not_in_schedule"] == ["Петров П.П."]

# Beeline не ответил по одному менеджеру: ручка всё равно доходит до конца
def test_activate_managers_beeline_error(client, test_db, monkeypatch):
    monkeypatch.setattr(callcenter, "load_month_schedule", lambda year, month: FAKE_SCHEDULE)

    def flaky_set_agent_status(shortnumber, status):
        if shortnumber == MANAGER_SECOND_NUMBER:
            raise requests.ConnectionError("Beeline не ответил")
        return status

    monkeypatch.setattr(callcenter,"set_agent_status", flaky_set_agent_status)

    response = client.post("/api/v1/activatemanagersonday")

    assert response.status_code == 200
    body = response.json()
    oks = {result["name"]: result["ok"] for result in body["results"]}
    assert oks == {"Иванов И.И.": True, "Петров П.П.": False}


# График недоступен: ручка отвечает ошибкой и никого не переключает
@pytest.mark.parametrize("error, expected_status", [
    (ScheduleNotFoundError, 503),
    (ScheduleUnavailableError, 503),
    (ScheduleOpenError, 500),
    (MonthNotFoundError, 404),
])
def test_activate_managers_schedule_error(client, test_db, beeline_calls, monkeypatch, error, expected_status):
    def broken_load_month_schedule(year, month):
        raise error("тестовая ошибка графика")

    monkeypatch.setattr(callcenter, "load_month_schedule", broken_load_month_schedule)

    response = client.post("/api/v1/activatemanagersonday")

    assert response.status_code == expected_status
    assert beeline_calls == []


# График читается за текущий месяц, если параметры не переданы
def test_receiving_dates_default_month(client, monkeypatch):
    calls = []

    def fake_load_month_schedule(year, month):
        calls.append((year, month))
        return FAKE_SCHEDULE

    monkeypatch.setattr(callcenter, "load_month_schedule", fake_load_month_schedule)

    response = client.get("/api/v1/receivingdatesfromexcel")

    today = date.today()
    assert response.status_code == 200
    assert calls == [(today.year, today.month)]
    assert response.json()["schedule"] == FAKE_SCHEDULE


# Год и месяц из параметров запроса доходят до чтения графика
def test_receiving_dates_with_params(client, monkeypatch):
    calls = []

    def fake_load_month_schedule(year, month):
        calls.append((year, month))
        return FAKE_SCHEDULE

    monkeypatch.setattr(callcenter, "load_month_schedule", fake_load_month_schedule)

    response = client.get("/api/v1/receivingdatesfromexcel?year=2025&month=3")

    assert response.status_code == 200
    assert calls == [(2025, 3)]


# Несуществующий месяц отклоняется до чтения графика
def test_receiving_dates_invalid_month(client):
    response = client.get("/api/v1/receivingdatesfromexcel?month=13")

    assert response.status_code == 422


# Ошибки графика превращаются в те же коды, что и у активации
@pytest.mark.parametrize("error, expected_status", [
    (ScheduleNotFoundError, 503),
    (ScheduleUnavailableError, 503),
    (ScheduleOpenError, 500),
    (MonthNotFoundError, 404),
])
def test_receiving_dates_schedule_error(client, monkeypatch, error, expected_status):
    def broken_load_month_schedule(year, month):
        raise error("тестовая ошибка графика")

    monkeypatch.setattr(callcenter, "load_month_schedule", broken_load_month_schedule)

    response = client.get("/api/v1/receivingdatesfromexcel")

    assert response.status_code == expected_status