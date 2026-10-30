from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# Импорт локального веб сервера
import uvicorn


# Импорт lifespan
from functions.startfunctions import lifespan, createdirs
# Импорт роутера для проверки доступности сервиса
from routers.checkstatus import check_status
# Импорт роутера для call центра
from routers.callcenter import call_center
'''
# Импорт роутера для проверки актуальности файлов
from routers.uptodatefiles import uptodatefiles
# Импорт роутера для выполнения действий в 1С
from routers.updatefilein1c_7_3 import uptodatefilesin1c
# Импорт роутера для сбора различной статистики
from routers.statistics import statcollection
# Импорт роутера для работы с фотографиями
from routers.photos import photos
# Импорт роутера для работы с Авито
from routers.avito import avito
# Импорт роутера для работы с Дром
from routers.drom import drom
# Импорт роутера для работы с Базой данных
from routers.database import database
'''

def routers(app: FastAPI) -> None:

    # Подключаем роутеры
    app.include_router(check_status, prefix="/api/v1", tags=["CheckStatus"])
    app.include_router(call_center, prefix="/api/v1", tags=["CallCenter"])
    '''
    app.include_router(uptodatefiles, prefix="/api/v1", tags=["UpToDatesFiles"])
    app.include_router(uptodatefilesin1c, prefix="/api/v1", tags=["UpToDatesFilesIn1C7.3"])
    app.include_router(database, prefix="/api/v1", tags=["DataBase"])
    app.include_router(statcollection, prefix="/api/v1", tags=["Statistics"])
    app.include_router(photos, prefix="/api/v1", tags=["Photos"])
    app.include_router(avito, prefix="/api/v1", tags=["Avito"])
    app.include_router(drom, prefix="/api/v1", tags=["Drom"])
    '''

def mainapp() -> FastAPI:
    # Создаем папки:
    createdirs()
    # Объявление основного приложения
    app = FastAPI(
        title="GlessGroup FastApi",
        description="Документация для сервиса GlessGroup.",
        version="1.1.0",
        docs_url="/documentaion",
        lifespan=lifespan)

    app.mount("/static", StaticFiles(directory = "static"), name = "static")

    # Прописываем роутеры
    routers(app)

    return app
if __name__ == "__main__":
    # Запускаем Uvicorn сервер
    uvicorn.run("main:mainapp", factory = True, reload = True)

