# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека для логгирования
# Импорт библиотеки для выполнения запросов
import requests
# Импорт библиотеки для работы с json
import json
# Библиотека для работы со временем
import datetime

# Импорт класса для работы с Авито
from dates import datesforavito
# Импорт класса для оповещения отвественных
from functions.logger import send_message_telegram_bot
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
@avito.get("/getcurrentbalance", summary="Получение баланса аккаунта Авито")
def get_current_balance():
    try:
        url = "https://api.avito.ru/cpa/v3/balanceInfo"
        Headers = dict()
        Headers["Authorization"] = get_access_token()["data"]
        Headers["X-Source"] = "BotGless2"
        Headers["Content-Type"] = "application/json"
        response = requests.Session().post(url, headers=Headers, json={})
        balance = response.json().get('balance') // 100
        return {
            "result": f"Баланс аккаунта получен",
            "data": balance}
    except Exception as e:
        return {
            "result": f"Сбой запроса токена авторизации",
            "data": e}

# Ручка вычисления средних трат на день
# Без входных аргументов
@avito.get("/calcavaragedaily", summary="Вычисление средних трат на день")
def calc_avarage_daily():
    try:
        # Количество средств потраченных за июнь 2025
        spent_money = 44200
        # Количество дней
        count_days = 30
        # Средние траты в день
        average_spent = spent_money // count_days
        return {
            "result": f"Средние траты в день",
            "data": average_spent}
    except Exception as e:
        return {
            "result": f"Сбой вычисления средних трат на день",
            "data": e}

# Ручка принятия решения по оповещению ответственных
# Без входных аргументов
@avito.get("/decisionmaking", summary="Принятие решения по оповещению ответственных")
def decision_making():
    try:
        # Получение баланса
        balance = get_current_balance()
        # Средние траты за день
        avmoney = calc_avarage_daily()
        # Определяем количество дней
        countdays = int(int(balance['data']) // avmoney['data'])
        # Текст сообщения
        textmessage = "Баланс Авито: " + str((balance['data'])) + " ₽\n"
        textmessage += "Баланса кошелька зватит на " + str(countdays) + " дней.\n\n"
        # Класс оповещения ответственных
        classnotification = send_message_telegram_bot()
        # Время сейчас
        today = datetime.datetime.today().strftime("%H:%M:%S")
        # Если денег хватит на меньше чем 3 дня
        if countdays <= 3:
            # Текст оповещения
            textmessage += "🔴Необходимо пополнить баланс.🔴"
        else:
            # Текст оповещения
            textmessage += "🟢Нет необходимости пополнять баланс.🟢"
        # Оповещения отвественных
        classnotification.notificationavito(textmessage)
        return {
            "result": f"Оповещение ответственных произведено",
            "data": True}

    except Exception as Ex:
        return {
            "result": f"Сбой вычисления средних трат на день",
            "data": str(Ex)}