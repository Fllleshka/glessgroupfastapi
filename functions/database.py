# Импорт библиотеки для работы с базой данных
import sqlite3
# Импорт библиотеки для работы с файлами
import os
# Импорт библиотеки для создания файлов xml
import xml.etree.ElementTree as ET

# Импорт данных путей к файлам
from dates import pathsfiles
# Импорт класса для фраз к прайс-листам
from dates import textforpricelists

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

# Проверка нахождения файла в папке
def checkphotoinfolder(folder, id, pathfolder):
    namephoto1 = str(id) + ".jpg"
    namephoto2 = str(id) + ".JPG"
    newpath = folder + str(pathfolder) + "/"
    if namephoto1 in os.listdir(newpath):
        #print("Нашёл!")
        return True
    elif namephoto2 in os.listdir(newpath):
        #print("Нашёл2!")
        return True
    else:
        #print(f"Ищем {id}\tв\t{pathfolder}\t\t{os.listdir(newpath)}")
        return False

# Функция генерации url картинок
def createtextsphotos(id_in_1C):
    # Путь к
    pathmainfolder = pathsfiles.sitefolder
    massfolders = os.listdir(pathmainfolder)
    resulttext = ""
    for elem in massfolders:
        if checkphotoinfolder(pathmainfolder, id_in_1C, elem) is True:
            resulttext += pathsfiles.pathsitefolder + str(elem) + "/" + str(id_in_1C) + ".jpg,"
    return resulttext

# Функция добавления данных в файл
def insertdatesinxml(root, element):
    # Добавляем дочерный элемент
    offer = ET.SubElement(root, "offer")
    # Номер в 1С
    addstr(offer, "Артикул", element[1])
    # print("\tarticle\t", element[1], "\t\t\t", )
    # Название товара в 1С
    addstr(offer, "Наименование_товара", element[2])
    # print("\tname\t", element[2])
    # Состояние новый или б/у
    addstr(offer, "Новый_БУ", element[9])
    # print("\tstate\t", element[9])
    # Марка производителя
    addstr(offer, "Марка", element[4])
    # print("\tbrand\t", element[4])
    # Модели автомобилей
    addstr(offer, "Модель", element[5])
    # print("\tmodel\t", element[5])
    # Кузова автомобилей
    addstr(offer, "Кузов", element[6])
    # print("\tbody\t", element[6])
    # Каталожный номер автомобилей
    addstr(offer, "Номер", element[11])
    # print("\tnumber\t", element[11])
    # Двигатели автомобилей
    addstr(offer, "Двигатель", element[8])
    # print("\tengine\t", element[8])
    # Года автомобилей
    addstr(offer, "Год", element[7])
    # print("\tyears\t", element[7])
    # Года автомобилей
    addstr(offer, "Производитель", element[10])
    # print("\tproducer\t", element[10])
    # Сторона автомобиля
    addstr(offer, "L-R", element[12])
    # print("\tside\t", element[12])
    # Перед/зад автомобиля
    addstr(offer, "F-R", element[13])
    # print("\tfront_back\t", element[13])
    # Количество штук
    addstr(offer, "Количество", element[14])
    # print("\tamount\t", element[14])
    # Цена
    if element[16] == "Под Заказ":
        addstr(offer, "Цена", 0)
    else:
        addstr(offer, "Цена", element[15])
    # Наличие
    addstr(offer, "Наличие", element[16])
    # Описание
    newdescription = textforpricelists.initialphrase
    if len(element[17]) == 0:
        newdescription += textforpricelists.middlerase
    else:
        newdescription += str(element[17])
    newdescription += textforpricelists.endphrase
    addstr(offer, "Описание", newdescription)
    # Фотографии
    textphoto = createtextsphotos(element[1])
    addstr(offer, "Ссылка_на_фото", textphoto)
    # Условие добавления данных при формировании прайс-листа под заказ
    if element[16] == "Под Заказ":
        addstr(offer, "supplier", "ИП Секачёв Станислав Юрьевич")
        addstr(offer, "supplier_inn", "550200540834")
        addstr(offer, "sklad", "г. Омск, ул. Лизы Чайкиной, д.7к3")
        addstr(offer, "supplier_art", element[1])

# Функция добавления строки в файл
def addstr(row, namecolumn, datecolumn):
    data = ET.SubElement(row, namecolumn)
    match (namecolumn):
        case "Новый_БУ":
            if datecolumn == "Квитанция комитента":
                data.text = "Б/У"
            else:
                data.text = str(datecolumn)
        case "L-R" | "F-R":
            if datecolumn is None:
                data.text = " "
            elif datecolumn == "":
                data.text = " "
            else:
                data.text = str(datecolumn)
        case _:
            if datecolumn == "":
                data.text = " "
            else:
                data.text = str(datecolumn)