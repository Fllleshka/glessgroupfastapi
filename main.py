# Импорт основной библиотеки FastAPI
from fastapi import FastAPI
# Импорт локального веб сервера
import uvicorn
# Библиотека для логирования
import logging
# Импорт роутера для call центра
from routers.callcenter import call_center
# Импорт роутера для проверки актуальности файлов
from routers.uptodatefiles import uptodatefiles
# Импорт роутера для сбора различной статистики
from routers.statistics import statcollection
# Импорт роутера для работы с фотографиями
from routers.photos import photos
# Импорт роутера для работы с фотографиями
from routers.avito import avito


# Объявление основного приложения
app = FastAPI()

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Подключаем роутеры
app.include_router(call_center, prefix="/api/v1", tags=["CallCenter"])
app.include_router(uptodatefiles, prefix="/api/v1", tags=["UpToDatesFiles"])
app.include_router(statcollection, prefix="/api/v1", tags=["Statistics"])
app.include_router(photos, prefix="/api/v1", tags=["Photos"])
app.include_router(avito, prefix="/api/v1", tags=["Avito"])

if __name__ == "__main__":
    uvicorn.run("main:app")