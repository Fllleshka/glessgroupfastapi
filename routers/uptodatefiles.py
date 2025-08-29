# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека работы с датой и временем
import datetime

# Импорт функции которая отвечает за принятие решения
from functions.uptodate import getlastmodifieddate, decisionmaking
# Импорт класса для отправки сообщения в Telegram
from functions.logger import class_send_erorr_message
# Импорт данных для работы телеграмм бота
from dates import telegrambot
# Импорт данных путей к файлам
from dates import pathsfiles

# Объявления роутер колл центра
uptodatefiles = APIRouter()

# Ручка для проверки актуальности файла базы данных
@uptodatefiles.get("/uptodatedatabase", summary="Проверка актуальности базы данных")
def up_to_date_database():
    # Путь к файлу базы данных
    pathtodatabase = pathsfiles.pathtodatabase
    # Получаем сегодняшнюю дату
    today = datetime.datetime.today()
    # Получаем дату последнего изменения файла
    lasttimeupdate = getlastmodifieddate(pathtodatabase)
    # Вызываем функцию принятия решения
    result = decisionmaking(pathtodatabase, lasttimeupdate)
    # Оповещение ответственного лица, что файлы не обновились
    if result == True:
        time = today.strftime("%H:%M")
        text = f"Файл базы данных\n[{pathtodatabase}]\nНе обновился."
        exception = "NoException"
        botkey = telegrambot.botkey
        notification = class_send_erorr_message(time, text, exception, botkey)
        notification.send_message()
    return {"todaydata": {today.strftime("%d.%m.%Y %H:%M:%S")},
            "lastdataupdatefile": {lasttimeupdate.strftime("%d.%m.%Y %H:%M:%S")},
            "decision": result
            }

# Ручка для проверки актуальности файла дром
@uptodatefiles.get("/uptodatedrom", summary="Проверка актуальности файла Дром")
def up_to_date_file_drom():
    # Путь к файлу базы данных
    pathtodatabase = pathsfiles.pathtodrom
    # Получаем сегодняшнюю дату
    today = datetime.datetime.today()
    # Получаем дату последнего изменения файла
    lasttimeupdate = getlastmodifieddate(pathtodatabase)
    # Вызываем функцию принятия решения
    result = decisionmaking(pathtodatabase, lasttimeupdate)
    # Оповещение ответственного лица, что файлы не обновились
    if result == True:
        time = today.strftime("%H:%M")
        text = f"Файл прайс листа для Дром\n[{pathtodatabase}]\nНе обновился."
        exception = "NoException"
        botkey = telegrambot.botkey
        notification = class_send_erorr_message(time, text, exception, botkey)
        notification.send_message()
    return {"todaydata": {today.strftime("%d.%m.%Y %H:%M:%S")},
            "lastdataupdatefile": {lasttimeupdate.strftime("%d.%m.%Y %H:%M:%S")},
            "decision": result
            }

# Ручка для проверки актуальности файла Авито
@uptodatefiles.get("/uptodateavito", summary="Проверка актуальности файла Авито")
def up_to_date_file_avito():
    # Путь к файлу базы данных
    pathtodatabase = pathsfiles.pathtoavito
    # Получаем сегодняшнюю дату
    today = datetime.datetime.today()
    # Получаем дату последнего изменения файла
    lasttimeupdate = getlastmodifieddate(pathtodatabase)
    # Вызываем функцию принятия решения
    result = decisionmaking(pathtodatabase, lasttimeupdate)
    # Оповещение ответственного лица, что файлы не обновились
    if result == True:
        time = today.strftime("%H:%M")
        text = f"Файл прайс листа для Авито\n[{pathtodatabase}]\nНе обновился."
        exception = "NoException"
        botkey = telegrambot.botkey
        notification = class_send_erorr_message(time, text, exception, botkey)
        notification.send_message()
    return {"todaydata": {today.strftime("%d.%m.%Y %H:%M:%S")},
            "lastdataupdatefile": {lasttimeupdate.strftime("%d.%m.%Y %H:%M:%S")},
            "decision": result
            }

# Ручка для проверки актуальности файла 2gis
@uptodatefiles.get("/uptodatedoublegis", summary="Проверка актуальности файла 2gis")
def up_to_date_file_double_gis():
    # Путь к файлу базы данных
    pathtodatabase = pathsfiles.pathdoublegis
    # Получаем сегодняшнюю дату
    today = datetime.datetime.today()
    # Получаем дату последнего изменения файла
    lasttimeupdate = getlastmodifieddate(pathtodatabase)
    # Вызываем функцию принятия решения
    result = decisionmaking(pathtodatabase, lasttimeupdate)
    # Оповещение ответственного лица, что файлы не обновились
    if result == True:
        time = today.strftime("%H:%M")
        text = f"Файл прайс листа для 2gis\n[{pathtodatabase}]\nНе обновился."
        exception = "NoException"
        botkey = telegrambot.botkey
        notification = class_send_erorr_message(time, text, exception, botkey)
        notification.send_message()
    return {"todaydata": {today.strftime("%d.%m.%Y %H:%M:%S")},
            "lastdataupdatefile": {lasttimeupdate.strftime("%d.%m.%Y %H:%M:%S")},
            "decision": result
            }

# Ручка для проверки актуальности файлов
@uptodatefiles.get("/uptodatedatabaseprices", summary="Проверка актуальности файла базы данных и прайс-листов")
def up_to_dates_database_prices():
    # Путь к файлу базы данных
    pathtofiles = [pathsfiles.pathtodatabase, pathsfiles.pathtodrom, pathsfiles.pathtoavito, pathsfiles.pathdoublegis]
    # Пути к текстам
    textstofiles = [pathsfiles.textdatabase, pathsfiles.textdrom, pathsfiles.pathtoavito, pathsfiles.textdoblegis]
    # Получаем сегодняшнюю дату
    today = datetime.datetime.today()
    index = 0
    directions = []
    # Перебираем все файлы
    for element in pathtofiles:
        lasttimeupdate = getlastmodifieddate(element)
        result = decisionmaking(element , lasttimeupdate)
        directions.append(result)
        # Оповещение ответственного лица, что файлы не обновились
        if result == True:
            time = today.strftime("%H:%M")
            text = textstofiles[index]
            exception = "NoException"
            botkey = telegrambot.botkey
            notification = class_send_erorr_message(time, text, exception, botkey)
            notification.send_message()
            index += 1
    return {"todaydata": {today.strftime("%d.%m.%Y %H:%M:%S")},
            "lastdataupdatefile": {lasttimeupdate.strftime("%d.%m.%Y %H:%M:%S")},
            "decision_database": directions[0],
            "decision_drom": directions[1],
            "decision_avito": directions[2],
            "decision_2gis": directions[3]
            }