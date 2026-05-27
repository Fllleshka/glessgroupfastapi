# Импорт класса для тестирования
from fastapi.testclient import TestClient
# Импорт класса для массива сотрудников
from dates import allsotr

from main import app
client = TestClient(app)

def test_online_user_call_center():

    for elem in range(200,210):
        request = "/api/v1/inclusion/" + str(elem)
        print(request)
        response = client.get(request)
        print(response)

        '''if str(elem) in allsotr.numbermanagers:
            print(f"ELEM: {elem} найден")
            print(response.json()['data'])
            assert response.status_code == 200
            #assert response.json()['data'] == 'ONLINE'
        else:
            print("Не найдено")
            print(response.json()['data'])
            assert response.status_code == 200
            #assert response.json()['data'] == 'Такого номера нету в Базе Данных'
'''
