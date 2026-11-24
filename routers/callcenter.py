# Импорт основной библиотеки FastAPI
import requests
from fastapi import APIRouter, Depends, HTTPException
# Библиотека для логгирования
import logging
# Модуль для работы с сесией базы данных
from sqlalchemy.orm import Session


# Импорт данных из базы
from database.repository import get_manager_by_shortnumber
from database.engine import get_users_session
# Импорт модуля выполнения запросов к API Beeline
from services.beeline import set_agent_status

#from dates import allsotr, beeline
# Импорт вспомогательных функций работы с Excel
#from functions.excel import importdatesformexcel
#from functions.excel import chosedates
#from functions.excel import checkupdatedatesexcel
#from functions.excel import readprotectedfile
#from functions.excel import writecopyfile
# Импорт функций логирования
#from functions.logger import class_logging_info_in_GoogleSheet
# Модель возврата результата
from schemas.modelresponse import CallCenterResponse

# Объявления роутер колл центра
call_center = APIRouter()
# Объявление логгера
logger = logging.getLogger(__name__)

# Ручка для включения сотрудника в колл центре
# Принимаем короткий номер сотрудника
@call_center.get("/inclusion/{user_id}", response_model= CallCenterResponse, summary="Включение сотрудника в call центре")
def online_user_call_center(user_id: int, session: Session = Depends(get_users_session)):
    logger.info(f"Вызван метод [Включение сотрудника в call центре]. Параметр входной: {user_id}")

    resultsearch = get_manager_by_shortnumber(session, user_id)

    if resultsearch is None:
        logger.info(f"Выполнение не может быть завершено. Пользователя: {user_id} не существует в данной системе")
        raise HTTPException(status_code=404, detail="Такого номера нету в Базе Данных")
    try:
        # Включаем менеджера
        agent_status = set_agent_status(user_id, "ONLINE")
    except requests.RequestException as e:
        logger.exception("Выполнение запроса завершилось с ошибкой.")
        raise HTTPException(status_code=502,
                            detail="Сервис Beeline недоступен. Статус не поменялся") from e
    return CallCenterResponse(
        result=True,
        status=agent_status,
        comment="Выполнено")

# Ручка для выключения сотрудника в колл центре
# Принимаем короткий номер сотрудника
@call_center.get("/shutdown/{user_id}", response_model = CallCenterResponse, summary="Выключение сотрудника в call центре")
def offline_user_call_center(user_id: int, session: Session = Depends(get_users_session)):
    logger.info(f"Вызван метод [Выключение сотрудника в call центре]. Параметр входной: {user_id}")

    resultsearch = get_manager_by_shortnumber(session, user_id)

    if resultsearch is None:
        logger.info(f"Выполнение не может быть завершено. Пользователя: {user_id} не существует в данной системе")
        raise HTTPException(status_code=404, detail="Такого номера нету в Базе Данных")
    try:
        # Выключаем менеджера
        agent_status = set_agent_status(user_id, "OFFLINE")
    except requests.RequestException as e:
        logger.exception("Выполнение запроса завершилось с ошибкой.")
        raise HTTPException(status_code=502,
                            detail="Сервис Beeline недоступен. Статус не поменялся") from e
    return CallCenterResponse(
        result=True,
        status=agent_status,
        comment="Выполнено")
'''
# Ручка получения актуальных данных из файла Excel
# Без входных аргументов
@call_center.get("/receivingdatesfromexcel", summary="Получение данных из Excel")
def receiving_dates_from_excel():
    logging.info(f"Вызван метод [Получение данных из Excel]")

    mainfile = readprotectedfile(datesforexcelfiles.pathmainfile, datesforexcelfiles.password)
    writecopyfile(mainfile, datesforexcelfiles.pathfile)

    try:
        # Достаём данные из файла
        datesnowmonth = importdatesformexcel(datesforexcelfiles.pathfile, datesforexcelfiles.password)
        # Выбираем данные для работы с ними
        massive = chosedates(datesnowmonth, allsotr)

        return {
            "result": "Данные из Excel получены успешно",
            "data": "massive"}
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
'''