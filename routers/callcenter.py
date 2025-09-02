# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека для логгирования
import logging
# Библиотека для работы с HTTP запросами
import requests
# Библиотека работы с датой и временем
import datetime

# Импорт данных
from dates import allsotr, beeline, datesforexcelfiles
# Импорт вспомогательных функций работы с Excel
from functions.excel import importdatesformexcel, chosedates, checkupdatedatesexcel
# Импорт функций логгирования
from functions.logger import class_logging_info_in_GoogleSheet
# Объявления роутер колл центра
call_center = APIRouter()

# Ручка для включения сотрудника в колл центре
# Принимаем короткий номер сотрудника
@call_center.get("/inclusion/{user_id}", summary="Включение сотрудника в call центре")
def online_user_call_center(user_id: str):
    logging.info(f"Вызван метод [Включение сотрудника в call центре]: {user_id}")
    # Поиск id в массиве коротких номеров менеджеров
    if user_id in allsotr.numbermanagers:
        # Запрос статуса во внешнем API
        urlforapi = beeline.urlapi + user_id + '/agent'
        # Попытка включения
        try:
            requests.put(urlforapi, params = beeline.paramsonline, headers = beeline.headers)
            # Возвращаем актуальный статус
            statusget = requests.get(urlforapi, headers=beeline.headers)
            return {
                "result": f"Статус менеджера: {user_id} изменён. Статус сейчас: {statusget.text}",
                "data": "ONLINE"}
        except Exception:
            return {
                "result": "Попытка включения завершилась ошибкой",
                "data": Exception}
    else:
        # Возврат если не верно указан короткий номер пользователя
        return {"result": "Пользователь не найден",
                "data": "Такого номера нету в Базе Данных"}

# Ручка для выключения сотрудника в колл центре
# Принимаем короткий номер сотрудника
@call_center.get("/shutdown/{user_id}", summary="Выключение сотрудника в call центре")
def offline_user_call_center(user_id: str):
    logging.info(f"Вызван метод [Выключение сотрудника в call центре]: {user_id}")
    # Поиск id в массиве коротких номеров менеджеров
    if user_id in allsotr.numbermanagers:
        # Запрос статуса во внешнем API
        urlforapi = beeline.urlapi + user_id + '/agent'
        # Попытка включения
        try:
            requests.put(urlforapi, params = beeline.paramoffline, headers = beeline.headers)
            # Возвращаем актуальный статус
            statusget = requests.get(urlforapi, headers=beeline.headers)
            return {
                "result": f"Статус менеджера: {user_id} изменён. Статус сейчас: {statusget.text}",
                "data": "OFFLINE"}
        except Exception:
            return {
                "result": "Попытка включения завершилась ошибкой",
                "data": Exception}
    else:
        # Возврат если не верно указан короткий номер пользователя
        return {"result": "Пользователь не найден",
                "data": "Такого номера нету в Базе Данных"}

# Ручка получения актуальных данных из файла Excel
# Без входных аргументов
@call_center.get("/receivingdatesfromexcel", summary="Получение данных из Excel")
def receiving_dates_from_excel():
    logging.info(f"Вызван метод [Получение данных из Excel]")
    try:
        # Достаём данные из файла
        datesnowmonth = importdatesformexcel(datesforexcelfiles.pathfile, datesforexcelfiles.password)
        # Выбираем данные для работы с ними
        massive = chosedates(datesnowmonth, allsotr)

        return {
            "result": "Данные из Excel получены успешно",
            "data": massive}
    except Exception:

        return {
            "result": "При получении данных произошла ошибка",
            "data": Exception}

# Ручка активации менеджеров на сегодня
# Без входных аргументов
@call_center.get("/activatemanagersonday", summary="Активация менеджеров на сегодня")
def activate_managers_on_day():
    logging.info(f"Вызван метод [Активация менеджеров на сегодня]")
    # Выясняем текущий день
    today = datetime.datetime.today()
    todayday = int(today.strftime("%d"))
    logging.info(f"Сегодня: {todayday} {today.strftime("%B")} {int(today.strftime("%Y"))}")
    try:
        dates = receiving_dates_from_excel()
        # Пробегаемся по массиву менеджеров
        for element in dates['data']:
            if element[todayday] == "В" or element[todayday] == "O" or element[todayday] == "О" or element[todayday] == "Х":
                numbermanager =  allsotr.numbermanagers[allsotr.massmanagers_short.index(element[0])]
                logging.info(f"\t\tНеобходимо деактивировать телефон: {element[0]}\t [{element[todayday]}]\t {numbermanager}")
                offline_user_call_center(numbermanager)
            else:
                numbermanager = allsotr.numbermanagers[allsotr.massmanagers_short.index(element[0])]
                logging.info(f"\t\tНеобходимо активировать телефон: {element[0]}\t [{element[todayday]}]\t {numbermanager}")
                online_user_call_center(numbermanager)
        class_log = class_logging_info_in_GoogleSheet()
        class_log.logging_update_call_center()
        return {
            "result": "Активация менеджеров на сегодня прошла успешно",
            "data": True}

    except Exception:
        return {
            "result": "Активации менеджеров произошла ошибка",
            "data": Exception}

# Ручка для копирования файла для работы
# Без входных аргументов
@call_center.get("/updatingexcelfile", summary="Актуализация данных в файле Excel для работы")
def update_excel_file():
    logging.info(f"Вызван метод [Актуализация данных в файле Excel для работы]")
    flag = checkupdatedatesexcel()
    if flag == True:
        text = "Актуализация данных в файле Excel для работы прошла успешно"
    else:
        text = "Актуализация файла не понадобилась"
    return {
        "result": text,
        "data": flag}
