"""Тесты сервиса Beeline: set_agent_status.

Настоящие запросы не выполняются: requests.put и requests.get подменяются функциями,
которые запоминают аргументы и возвращают заранее подготовленный ответ.
Настройки (.env) тоже подменяются, поэтому тесты работают и на GitHub, где .env нет.
"""
from types import SimpleNamespace

import pytest
import requests
from pydantic import SecretStr

from services import beeline

API_URL = "https://beeline.test/agents/"
HEADER_NAME = "X-Test-Token"
TOKEN = "test-token"
MANAGER_NUMBER = 105


# Собирает настоящий объект ответа requests.
# В отличие от MagicMock, у него по-настоящему работают raise_for_status() и json().
def make_response(status_code: int, body: bytes = b"") -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = body
    response.url = API_URL
    return response


# Подмена настроек: вместо чтения .env — объект с тестовыми значениями.
# autouse=True — фикстура включается для каждого теста в этом файле автоматически.
@pytest.fixture(autouse=True)
def fake_settings(monkeypatch):
    settings = SimpleNamespace(
        beeline_api_url=API_URL,
        beeline_header_name=HEADER_NAME,
        beeline_token=SecretStr(TOKEN),
    )
    monkeypatch.setattr(beeline, "get_settings", lambda: settings)


# Подмена HTTP-запросов. По умолчанию Beeline отвечает успешно и возвращает "ONLINE".
# Тест может заменить ответ: fake_http.responses["put"] = make_response(401)
@pytest.fixture
def fake_http(monkeypatch):
    calls = {"put": [], "get": []}
    responses = {
        "put": make_response(200),
        "get": make_response(200, b'"ONLINE"'),
    }

    def fake_put(url, **kwargs):
        calls["put"].append((url, kwargs))
        return responses["put"]

    def fake_get(url, **kwargs):
        calls["get"].append((url, kwargs))
        return responses["get"]

    monkeypatch.setattr(beeline.requests, "put", fake_put)
    monkeypatch.setattr(beeline.requests, "get", fake_get)
    return SimpleNamespace(calls=calls, responses=responses)


# Beeline отдаёт JSON-строку "ONLINE" с кавычками — функция возвращает ONLINE без кавычек
def test_returns_status_without_quotes(fake_http):
    result = beeline.set_agent_status(MANAGER_NUMBER, "ONLINE")

    assert result == "ONLINE"


# Проверяем, что уходит в Beeline: адрес, статус, заголовок с токеном, таймаут
@pytest.mark.parametrize("status", ["ONLINE", "OFFLINE"])
def test_sends_correct_request(fake_http, status):
    beeline.set_agent_status(MANAGER_NUMBER, status)

    expected_url = f"{API_URL}{MANAGER_NUMBER}/agent"
    expected_headers = {HEADER_NAME: TOKEN}

    assert fake_http.calls["put"] == [(expected_url, {
        "params": {"status": status},
        "headers": expected_headers,
        "timeout": 10,
    })]
    assert fake_http.calls["get"] == [(expected_url, {
        "headers": expected_headers,
        "timeout": 10,
    })]


# Beeline отказал при смене статуса (401): ошибка вылетает наружу, статус не запрашивается
def test_put_error_raises_and_skips_get(fake_http):
    fake_http.responses["put"] = make_response(401)

    with pytest.raises(requests.HTTPError):
        beeline.set_agent_status(MANAGER_NUMBER, "ONLINE")

    assert fake_http.calls["get"] == []


# Статус сменился, но запрос текущего статуса вернул 500: ошибка вылетает наружу
def test_get_error_raises(fake_http):
    fake_http.responses["get"] = make_response(500)

    with pytest.raises(requests.HTTPError):
        beeline.set_agent_status(MANAGER_NUMBER, "ONLINE")


# Beeline не ответил вовремя: Timeout не проглатывается
def test_timeout_raises(monkeypatch):
    def slow_put(url, **kwargs):
        raise requests.Timeout

    monkeypatch.setattr(beeline.requests, "put", slow_put)

    with pytest.raises(requests.Timeout):
        beeline.set_agent_status(MANAGER_NUMBER, "ONLINE")
