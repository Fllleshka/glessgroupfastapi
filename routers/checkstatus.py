# Импорт основной библиотеки FastAPI
from fastapi import APIRouter, Request, Response, status
# Импорт инструментов SQLAlchemy для проверки баз
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Импорт движков баз данных
from database.engine import usersdatabaseengine, productsdatabaseengine
# Импорт логгера
from functions.startfunctions import logger

# Объявление роутера для проверки состояния сервиса
check_status = APIRouter()

# Базы, которые проверяет /health: имя в ответе → (движок, таблица для проверки)
DATABASES = {
    "users": (usersdatabaseengine, "users"),
    "products": (productsdatabaseengine, "products"),
}


# Функция проверки одной базы данных
# Возвращает None, если база в порядке, или текст ошибки
def check_database(engine: Engine, table: str) -> str | None:
    try:
        with engine.connect() as connection:
            # Обращаемся к реальной таблице: SELECT 1 без таблицы прошёл бы
            # даже на пустом файле, который SQLite создаёт сам при подключении
            connection.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
        return None
    except SQLAlchemyError as e:
        return f"{e.__class__.__name__}: {e}"


# Ручка проверки, что процесс жив
@check_status.get("/", summary="Проверка статуса")
def checkstatus():
    logger.info("Функция проверки статуса отработала")
    return True


# Ручка проверки работоспособности сервиса и баз данных (для мониторинга и деплоя)
@check_status.get("/health", summary="Проверка сервиса и баз данных")
def health(request: Request, response: Response) -> dict:
    # Проверяем каждую базу
    errors = {name: check_database(engine, table) for name, (engine, table) in DATABASES.items()}
    databases = {name: "ok" if error is None else "error" for name, error in errors.items()}
    healthy = all(error is None for error in errors.values())

    # При сбое отдаём 503 и пишем подробности в лог (наружу — только "error")
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        failed = {name: error for name, error in errors.items() if error is not None}
        logger.error(f"Проверка /health не пройдена: {failed}")

    return {
        "status": "ok" if healthy else "error",
        "version": request.app.version,
        "databases": databases,
    }