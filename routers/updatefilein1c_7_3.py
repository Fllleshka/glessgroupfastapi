# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Импорт функции перемещения мышки
from functions.movemouse import movemouse

# Объявление роутера обновление файлов в 1С
uptodatefilesin1c = APIRouter()


# Ручка для проставления остатков на удалённом рабочем столе
@uptodatefilesin1c.get("/putdownbalances", summary="Проставить остатки")
def put_down_balances():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к вкладке "Проставить остатки"
    # [2] Перемещение к кнопке "Сформировать"
    # [3] Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 200, 100, 1100]
    massy = [1060, 540, 1005, 270, 10]
    try:
        movemouse(massx, massy, 3)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}

# Ручка для формирования файла xml
@uptodatefilesin1c.get("/formpricelist", summary="Формирование прайс-листа")
def form_price_list():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к вкладке "Выгрузка товаров на сайт"
    # [2] Перемещение к кнопке "Сформировать"
    # [3] # Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 400, 200, 1100]
    massy = [1060, 540, 1005, 200, 10]
    try:
        movemouse(massx, massy, 3)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}

# Ручка для подтверждения новой даты
@uptodatefilesin1c.get("/confirmnewdata", summary="Подтверждение новой даты")
def confirm_new_data():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к кнопке "Сменить рабочую дату"
    # [2] # Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 920, 1100]
    massy = [1060, 540, 570, 10]
    try:
        movemouse(massx, massy, 1)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}

# Ручка для закрытия файла с проставленными остатками
@uptodatefilesin1c.get("/closetable", summary="Закрытие файла с проставленными остатками")
def close_table():
    # [0] Перемещение к свёрнутому рабочему столу
    # [1] Перемещение к вкладке "Сформировать2"
    # [2] Перемещение к закрытию таблицы
    # [3] # Перемещение к сворачиванию удалённого рабочего стола
    massx = [260, 960, 800, 1910, 1100]
    massy = [1060, 540, 1005, 25, 10]
    try:
        movemouse(massx, massy, 3)
    except Exception as e:
        return {"result": e}
    else:
        return {"result": True}