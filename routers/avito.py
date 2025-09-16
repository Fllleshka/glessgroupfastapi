# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека для логгирования
import logging
# Импорт библиотеки для выполнения запросов
import requests
# Импорт библиотеки для работы с json
import json

# Импорт класса для работы с Авито
from dates import datesforavito
# Объявления роутер для работы с AvitoAPI
avito = APIRouter()

# Ручка для получения токена для работы
# Без входных аргументов
@avito.get("/getaccesstoken", summary="Получение TOKEN для работы")
def get_access_token():
    try:
        autourl = "https://api.avito.ru/token/"
        # Параметры запроса.
        Params = {
            "grant_type": "client_credentials",
            "client_id": datesforavito.autorization_id,
            "client_secret": datesforavito.autorization_secret
        }
        # Заголовки запроса
        Headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # Запрос нового токена доступа.
        # Сессия
        Response = requests.Session().post(autourl, headers=Headers, params=Params)
        jsonresp = dict(json.loads(Response.text))
        result = jsonresp["token_type"] + " " + jsonresp['access_token']
        return {
            "result": f"Токен авторизации получен",
            "data": result}
    except Exception as e:
        return {
            "result": f"Сбой запроса токена авторизации",
            "data": e}

# Ручка для получения баланса
# Без входных аргументов
@avito.get("/getcurrentbalance", summary="Получение баланса аккаунта авито")
def get_current_balance():
    try:
        url = "https://api.avito.ru/cpa/v3/balanceInfo"
        Headers = dict()
        Headers["Authorization"] = get_access_token()
        Headers["X-Source"] = "BotGless2"
        Headers["Content-Type"] = "application/json"
        response = requests.Session().post(url, headers=Headers, json={})
        print(response)
        balance = response.json().get('balance') // 100
        return {
            "result": f"Баланс аккаунта получен",
            "data": balance}
    except Exception as e:
        return {
            "result": f"Сбой запроса токена авторизации",
            "data": e}
