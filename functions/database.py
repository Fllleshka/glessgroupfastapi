# Импорт библиотеки для работы с базой данных
import sqlite3
# Импорт библиотеки для работы с файлами
import os

# Импорт данных путей к файлам
from dates import pathsfiles


# Функция поиска в таблице данный по 1C_id
def searchelemindatabase(id_in_1c):
    # Подключаемся к базе данных
    connection = sqlite3.connect(pathsfiles.pathtodatabase)
    cursor = connection.cursor()
    sql_request = "SELECT * FROM spare_part WHERE id_in_1c='" + str(id_in_1c) + "'"
    #print(sql_request)
    cursor.execute(sql_request)
    row = cursor.fetchone()
    # Завершаем работу с базой данных
    connection.close()
    if row == None:
        return False
    else:
        return True

# Функция обновления строки в базе данных
def updateindatabaserow(connection, cursor, dates):
    # Формирование SQL запроса
    sql_request = "UPDATE spare_part "
    sql_request += "SET name = '" + dates[1] + "', "
    if dates[2] == '':
        sql_request += "side = '" + "" + "', "
    else:
        sql_request += "side = '" + dates[2] + "', "
    sql_request += "brand = '" + dates[3] + "', "
    sql_request += "model = '" + dates[4] + "', "
    sql_request += "body = '" + dates[5] + "', "
    sql_request += "years = '" + dates[6] + "', "
    sql_request += "engine = '" + dates[7] + "', "
    sql_request += "state = '" + dates[8] + "', "
    sql_request += "producer = '" + dates[9] + "', "
    sql_request += "number = '" + dates[10] + "', "
    if dates[11] == None:
        sql_request += "side = '" + "" + "', "
    else:
        sql_request += "side = '" + dates[11] + "', "
    if dates[12] == None:
        sql_request += "side = '" + "" + "', "
    else:
        sql_request += "side = '" + dates[12] + "', "
    sql_request += "amount = '" + dates[13] + "', "
    sql_request += "price = '" + dates[14] + "', "
    sql_request += "availability = '" + dates[15] + "', "
    sql_request += "direction = '" + dates[16] + "', "
    sql_request += "new = '" + dates[17] + "', "
    sql_request += "name_internet = '" + dates[18] + "', "
    sql_request += "up_down = '" + dates[19] + "', "
    sql_request += "transmission = '" + dates[20] + "', "
    sql_request += "drive = '" + dates[21] + "', "
    sql_request += "type_body = '" + dates[22] + "', "
    sql_request += "synonim = '" + dates[23] + "' "
    sql_request += "WHERE id_in_1c = " + dates[0]

    # Вставка данных
    cursor.execute(sql_request)
    connection.commit()

# Функция вставки в базу строки
def insertintodatabasenewrow(connection, cursor, dates):
    print(dates)
    # Формирование SQL запроса
    sql_request = "INSERT INTO spare_part "
    sql_request += "(id_in_1c, name, tab, brand, model, body, years, engine, state, producer, number, side, front_back, "
    sql_request += "amount, price, availability, direction, new, name_internet, up_down, transmission, drive, type_body, synonim) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    # Вставка данных
    cursor.execute(sql_request, dates)
    connection.commit()

# Функция получения данных из базы
def selectalldatesfromdatabase():
    # Подключение к базе данных
    connection = sqlite3.connect(pathsfiles.pathtodatabase)
    cursor = connection.cursor()
    sqlrequest = "SELECT * FROM spare_part"
    cursor.execute(sqlrequest)
    dates = cursor.fetchall()
    # Отключение от базы данных
    connection.close()
    return dates

# Функция проверки статуса позиции "Под заказ"
def checkavailability(data):
    if data[16] == "Под Заказ":
        #print(data[16]," Товары под заказ не публикуем")
        return False
    else:
        #print(data[16]," Товары под заказ публикуем")
        return True

# Функция проверки на услуги
def checkproductname(data):
    if "Услуга" in data[2]:
        return False
    else:
        return True



