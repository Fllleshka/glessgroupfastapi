import pytest

URL = "/api/v1/"


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
