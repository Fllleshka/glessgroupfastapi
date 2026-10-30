# Импорт основной библиотеки FastAPI
from fastapi import APIRouter

from functions.startfunctions import logger
# Объявления роутер для работы с AvitoAPI
check_status = APIRouter()

# Ручка проверки статуса
@check_status.get("/", summary="Проверка статуса")
def checkstatus():
    logger.info("Функция проверки статуса отработала")
    return True