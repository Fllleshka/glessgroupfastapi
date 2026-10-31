import pytest
# Импорт данных
from dates import allsotr, beeline
from unittest.mock import patch, MagicMock

URL = "/api/v1/inclusion/"

# Производим подмену реального API
@pytest.fixture
def mocked_api():
    with patch("routers.callcenter.requests.put") as put_mock, \
         patch("routers.callcenter.requests.get") as get_mock:
        put_mock.return_value = MagicMock(status_code=200)
        get_mock.return_value = MagicMock(status_code=200, text='{"status":"ONLINE"}')
        yield put_mock, get_mock


# Проверяем тело ответа и вызовы API
@pytest.mark.parametrize("shortnumber", allsotr.numbermanagers)
def test_online_user_success(client, mocked_api, shortnumber):
    put_mock, get_mock = mocked_api

    response = client.get(URL + shortnumber)

    assert response.status_code == 200
    body = response.json()
    assert body["data"] == "ONLINE"
    assert shortnumber in body["result"]
    assert '{"status":"ONLINE"}' in body["result"]

    expected_url = beeline.urlapi + shortnumber + "/agent"
    put_mock.assert_called_once_with(
        expected_url, params=beeline.paramsonline, headers=beeline.headers
    )
    get_mock.assert_called_once_with(expected_url, headers=beeline.headers)


# Номера нет в allsotr.numbermanagers
@pytest.mark.parametrize("fake_number", ["0000", "999999", "abc", "-1", "800", "1010"])
def test_online_user_not_found(client, mocked_api, fake_number):
    put_mock, get_mock = mocked_api
    assert fake_number not in allsotr.numbermanagers  # защита от случайного совпадения

    response = client.get(URL + fake_number)

    assert response.status_code == 200
    assert response.json() == {
        "result": "Пользователь не найден",
        "data": "Такого номера нету в Базе Данных",
    }
    # во внешний API ходить не должны
    put_mock.assert_not_called()
    get_mock.assert_not_called()


# Ошибка внешнего API
def test_online_user_api_error(client):
    number = allsotr.numbermanagers[0]
    with patch("routers.callcenter.requests.put", side_effect=Exception("timeout")), \
         patch("routers.callcenter.requests.get") as get_mock:

        response = client.get(URL + number)

    assert response.status_code == 200
    assert response.json() == {
        "result": "Попытка включения завершилась ошибкой",
        "data": "timeout",
    }
    get_mock.assert_not_called()  # после падения put до get дело не доходит


# Номер, которого нет в реальном списке, но мы делаем его "существующим"
def test_online_user_custom_number(client, mocked_api, monkeypatch):
    monkeypatch.setattr(allsotr, "numbermanagers", ["7777"])

    response = client.get(URL + "7777")

    assert response.json()["data"] == "ONLINE"