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
from functions.excel import importdatesformexcel, chosedates

# Обьявления роутер колл центра
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
        return {
            "result": "Активация менеджеров на сегодня прошла успешно",
            "data": True}

    except Exception:
        return {
            "result": "Активации менеджеров произошла ошибка",
            "data": Exception}

    '''
    flag = True
    massworkmanagers = []
    try:
        # Изменяем статусы менеджеров call центра
        for element in managerlists:
            if element[todayday] == "В" or element[todayday] == "O" or element[todayday] == "О" or element[todayday] == "Х":
                #numbermanager = numbermanagers[massmanagers.index(element[0])]
                numbermanager =  allsotr.numbermanagers[allsotr.massmanagers_short.index(element[0])]
                print("\t\tНеобходимо деактивировать телефон: ", element[0], "\t[", element[todayday], "]", "'",
                      numbermanager,
                      "'")
                urlforapi = urlapi + str(numbermanager) + '/agent'
                statusrequest = requests.put(urlforapi, params=paramoffline, headers=headers)
                if statusrequest == "<Response [403]>":
                    flag = False
                    print("\tЧто-то пошло не так... Нет ответа по запросу изменения статуса")
                else:
                    statusget = requests.get(urlforapi, headers=headers).text
                    print("\tСтатус менеджера: ", element[0], " = ", statusget)
            else:
                #numbermanager = numbermanagers[massmanagers.index(element[0])]
                numbermanager = allsotr.numbermanagers[allsotr.massmanagers_short.index(element[0])]
                print("\t\tНеобходимо активировать телефон: ", element[0], "\t[", element[todayday], "]", "'",
                      numbermanager,
                      "'")
                urlforapi = urlapi + str(numbermanager) + '/agent'
                statusrequest = requests.put(urlforapi, params=paramsonline, headers=headers)
                if statusrequest == "<Response [403]>":
                    flag = False
                    print("\tЧто-то пошло не так... Нет ответа по запросу изменения статуса")
                else:
                    # Дополнительное условие для последнего менеджера
                    massworkmanagers.append(element[todayday])
                    if len(massworkmanagers) == 4:
                        # Если 3 других менеджера работают, то 4 должен быть отключён
                        if (massworkmanagers[0] == '9.0' or massworkmanagers[0] == '10.0') and (
                                massworkmanagers[1] == '9.0' or massworkmanagers[1] == '10.0') and (
                                massworkmanagers[2] == '9.0' or massworkmanagers[2] == '10.0'):
                            requests.put(urlforapi, params=paramoffline, headers=headers)
                    statusget = requests.get(urlforapi, headers=headers).text
                    print("\tСтатус менеджера: ", element[0], " = ", statusget)

        if flag == True:
            return "\tCall центр успешно настроен."
        else:
            return "\tВ работе функции произошла ошибка"
    except Exception as e:
        print(f"В работе call-центра произошла ошибка: {e}")

    return True
    '''