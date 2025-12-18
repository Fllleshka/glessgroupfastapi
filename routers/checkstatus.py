# Импорт основной библиотеки FastAPI
from fastapi import APIRouter

# Объявления роутер для работы с AvitoAPI
check_status = APIRouter()

# Ручка проверки статуса
@check_status.get("/", summary="Проверка статуса")
def checkstatus():
    return True