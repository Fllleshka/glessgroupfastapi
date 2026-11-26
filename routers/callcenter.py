# Импорт основной библиотеки FastAPI
from fastapi import APIRouter, Depends, HTTPException, Query
# Библиотека для логирования
import logging
# Модуль для работы с сессией базы данных
from sqlalchemy.orm import Session
#  Модуль для работы со временем
from datetime import date

import requests


# Импорт данных из базы
from database.repository import get_manager_by_shortnumber, get_callcenter_managers
from database.engine import get_users_session
# Импорт модуля выполнения запросов к API Beeline
from services.beeline import set_agent_status
# Импорт модуля для работы с файлом графика (excel)
from services.schedule import ScheduleNotFoundError, ScheduleUnavailableError, ScheduleOpenError, MonthNotFoundError
from services.schedule import load_month_schedule, status_for_day
# Модель возврата результата
from schemas.modelresponse import CallCenterResponse, ActivationResponse, ManagerStatusResult, ScheduleResponse

# Объявления роутер колл центра
call_center = APIRouter()
# Объявление логгера
logger = logging.getLogger(__name__)

# Загружает график месяца и превращает ошибки графика в HTTP-ответы
def get_schedule_or_http_error(year: int, month: int) -> dict[str, list[str]]:
    try:
        return load_month_schedule(year, month)
    except (ScheduleNotFoundError, ScheduleUnavailableError) as e:
        logger.exception("График недоступен")
        raise HTTPException(status_code=503, detail=str(e)) from e
    except ScheduleOpenError as e:
        logger.exception("Не удалось открыть график")
        raise HTTPException(status_code=500, detail=str(e)) from e
    except MonthNotFoundError as e:
        logger.exception("В графике нет нужного месяца")
        raise HTTPException(status_code=404, detail=str(e)) from e

# Ручка для включения сотрудника в колл центре
# Принимаем короткий номер сотрудника
@call_center.post("/inclusion/{user_id}", response_model= CallCenterResponse, summary="Включение сотрудника в call центре")
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
@call_center.post("/shutdown/{user_id}", response_model = CallCenterResponse, summary="Выключение сотрудника в call центре")
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

# Ручка получения актуальных данных из файла Excel
# Без входных аргументов
@call_center.get("/receivingdatesfromexcel", response_model=ScheduleResponse, summary="Получение данных из Excel")
def receiving_dates_from_excel(year: int | None = None, month: int | None = Query(default=None, ge=1, le=12)):
    logger.info(f"Вызван метод [Получение данных из Excel]")
    today = date.today()
    year = year or today.year
    month = month or today.month
    schedule = get_schedule_or_http_error(year, month)
    return ScheduleResponse(
        year=year,
        month=month,
        schedule=schedule)

# Ручка активации менеджеров на сегодня
# Без входных аргументов
@call_center.post("/activatemanagersonday", response_model=ActivationResponse, summary="Активация менеджеров на сегодня")
def activate_managers_on_day(session: Session = Depends(get_users_session)):
    logger.info(f"Вызван метод [Активация менеджеров на сегодня]")
    # Выясняем текущий день
    today = date.today()

    # Получаем данные из файла
    schedule = get_schedule_or_http_error(today.year, today.month)

    results = []
    not_in_schedule = []
    for manager in get_callcenter_managers(session):
        # Получаем статус менеджера
        status = status_for_day(schedule, manager.shortname, today.day)
        if status is None:
            logger.warning(f"{manager.shortname} нет в графике")
            not_in_schedule.append(manager.shortname)
        else:
            try:
                set_agent_status(manager.shortnumber, status)
                ok = True
            except requests.RequestException:
                logger.exception(f"Не удалось установить {status} для {manager.shortname}")
                ok = False
            results.append(ManagerStatusResult(
                name=manager.shortname,
                shortnumber=manager.shortnumber,
                status=status,
                ok = ok
            ))
    return ActivationResponse(
        date=today,
        results=results,
        not_in_schedule=not_in_schedule
    )