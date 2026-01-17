# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека работы с датой и временем
import datetime
import os.path
# Импорт функции которая отвечает за принятие решения
from functions.uptodate import getlastmodifieddate, decisionmaking
# Импорт класса для отправки сообщения в Telegram
from functions.logger import class_send_erorr_message
# Импорт функции перемещения мышки
from functions.movemouse import movemouse
# Импорт данных для работы телеграмм бота
from dates import telegrambot
# Импорт данных путей к файлам
from dates import pathsfiles

# Объявления роутер колл центра
uptodatefiles = APIRouter()

# Ручка для проверки актуальности файла базы данных
@uptodatefiles.get("/uptodatedatabase", summary="Проверка актуальности базы данных")
def up_to_date_database():
    if os.path.exists(pathsfiles.pathtodatabase):
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
                "decision": result}
    else:
        return {"decision": None}

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

# Ручка для проставления остатков на удалённом рабочем столе
@uptodatefiles.get("/putdownbalances", summary="Проставить остатки")
def put_down_balances():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к вкладке "Проставить остатки"
    # [2] Перемещение к кнопке "Сформировать"
    # [3] Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 200, 100, 1220]
    massy = [1060, 540, 1005, 270, 10]
    try:
        movemouse(massx, massy, 3)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}

# Ручка для формирования файла xml
@uptodatefiles.get("/formpricelist", summary="Формирование прайс-листа")
def form_price_list():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к вкладке "Выгрузка товаров на сайт"
    # [2] Перемещение к кнопке "Сформировать"
    # [3] # Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 400, 200, 1220]
    massy = [1060, 540, 1005, 200, 10]
    try:
        movemouse(massx, massy, 3)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}

# Ручка для подтверждения новой даты
@uptodatefiles.get("/confirmnewdata", summary="Подтверждение новой даты")
def confirm_new_data():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к кнопке "Сменить рабочую дату"
    # [2] # Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 920, 1220]
    massy = [1060, 540, 570, 10]
    try:
        movemouse(massx, massy, 1)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}

# Ручка для закрытия файла с проставленными остатками
@uptodatefiles.get("/closetable", summary="Закрытие файла с проставленными остатками")
def close_table():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к вкладке "Сформировать2"
    # [2] Перемещение к закрытию таблицы
    # [3] # Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 800, 1910, 1220]
    massy = [1060, 540, 1005, 25, 10]
    try:
        movemouse(massx, massy, 3)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}