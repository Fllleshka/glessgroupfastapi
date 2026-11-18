# Библиотека для логирования
import logging
# Библиотека для работы с каталогами
from pathlib import Path
# Библиотека для создания асинхронного контекст менеджера
from contextlib import asynccontextmanager

from fastapi import FastAPI

# Определяем корень проекта
basedir = Path(__file__).resolve().parent.parent
# Путь к папке с логами
logsdir = basedir / "logs"
# Путь к папке со статичными файлами
staticdir = basedir / "static"
# Обьявлем логгер для записи логов
logger = logging.getLogger(__name__)


# Функция создания папок
def createdirs() -> None:
    massfolders = [logsdir, staticdir]
    for folder in massfolders:
        folder.mkdir(parents=True, exist_ok=True)

# Функция настройки логирования
def createlogging() -> None:
    # Настройка для формата вывода
    fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    # Настройка для файла
    file_handler = logging.FileHandler(logsdir / "fastapi.log", mode="a",
                                       encoding="utf-8")
    file_handler.setFormatter(fmt)
    # Настройка для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    # Настройка самого логирования
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    root.addHandler(file_handler)
    root.addHandler(console_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем папки
    createdirs()
    # Настраиваем логирование
    createlogging()

    logger.info("Старт приложения")

    yield

    logger.info("Приложение остановлено")