import os.path
import sqlite3
import datetime
import xml.etree.ElementTree
from lxml import etree
import tqdm
# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Импорт данных путей к файлам
from dates import pathsfiles
# Импорт функции для поиска данных в базе
from functions.database import *
# Импорт библиотеки для создания файлов xml
import xml.etree.ElementTree as ET
# Импорт функций для генерации прайс-листов
from functions.exportfiles import insertdatesinxmldrom
from functions.exportfiles import insertdatesinxmlavito
from functions.exportfiles import insertdatesin2gis, indertdefautdatesin2gis
from functions.exportfiles import insertdatesinvk, indertdefautdatesinvk
# Объявления роутер колл центра
database = APIRouter()


# Ручка для инициализации работы с базой данных
@database.post("/initdatabasefile",
               summary="Инициализация файла базы данных")
def initdatabasefile():
    pathfile = pathsfiles.pathtodatabase
    # Выполняем проверку наличие на базы данных
    if os.path.exists(pathfile):
        return {"result": True}
    else:
        # Создаём базу данных
        file = open(pathfile, "w+")
        file.close()
        print("Файл базы данных успешно создан")

        # Подключаемся к базе данных
        connection = sqlite3.connect(pathfile)
        cursor = connection.cursor()

        # Создаём таблицу spare_part
        cursor.execute('''
                           CREATE TABLE spare_part(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               id_in_1c INTEGER,
                               name varchar(255) NOT NULL,
                               tab INTEGER,
                               brand varchar(255),
                               model varchar(255),
                               body varchar(255),
                               years varchar(255),
                               engine varchar(255),
                               state varchar(255),
                               producer varchar(255),
                               number varchar(255),
                               side varchar(255),
                               front_back varchar(255),
                               amount varchar(255),
                               price varchar(255),
                               availability varchar(255),
                               direction text,
                               new varchar(255),
                               name_internet varchar(255),
                               up_down varchar(255),
                               transmission varchar(255),
                               drive varchar(255),
                               type_body varchar(255),
                               synonim varchar(255)) 
                            ''')
        connection.commit()
        connection.close()
        '''< Элемент
            Вкладка = "6680"
            Наименование = "Can bus decjder, CX-7"
            Марка = "MAZDA"
            Модель = ""
            Кузов = "ER,"
            Год = "2006-2012,"
            Двигатель = ""
            НовыйИли = "Б/У"
            Производитель = "Китай"
            Номер = "MZD-SS-06"
            L - R = ""
            F - R = ""
            Количество = "0"
            Цена = "0"
            Наличие = "Под заказ"
            ID = "38838"
            Описание = ""
            Новинка = ""
            НаименованиеИнтернет = ""
            ВерхНиз = ""
            КПП = ""
            WD = ""
            ВидКузова = ""
            Синоним = "" / >'''

        today = datetime.datetime.today()

        return {
            "createdate": today.strftime("%d.%m.%Y %H:%M:%S"),
            "result": "Файл успешно создан"}


# Ручка ввода актуальных данных в базу
@database.post("/insertnewdatesindatabase",
               summary="Ввод актуальных данных в базу")
def insertnewdatesindatabase():
    # Время начала обработки
    starttime = datetime.datetime.today()

    # Подключаемся к базе данных
    connection = sqlite3.connect(pathsfiles.pathtodatabase)
    cursor = connection.cursor()

    # Разбор файла
    tree = xml.etree.ElementTree.parse(pathsfiles.exportfilefrom1c)
    root = tree.getroot()
    mass = root.iter()
    next(mass)

    # Формирование данных и вставка их в базу данных
    for elem in tqdm.tqdm(mass, desc='Processing'):
        list_dates = []
        id_in_1c = elem.attrib.get('ID')
        list_dates.append(id_in_1c)
        #name = elem.attrib.get('Наименование')
        list_dates.append(elem.attrib.get('Наименование'))
        #tab = elem.attrib.get('Вкладка')
        list_dates.append(elem.attrib.get('Вкладка'))
        #brand = elem.attrib.get('Марка')
        list_dates.append(elem.attrib.get('Марка'))
        #model = elem.attrib.get('Модель')
        list_dates.append(elem.attrib.get('Модель'))
        #body = elem.attrib.get('Кузов')
        list_dates.append(elem.attrib.get('Кузов'))
        #years = elem.attrib.get('Год')
        list_dates.append(elem.attrib.get('Год'))
        #engine = elem.attrib.get('Двигатель')
        list_dates.append(elem.attrib.get('Двигатель'))
        #state = elem.attrib.get('НовыйИли')
        list_dates.append(elem.attrib.get('НовыйИли'))
        #producer = elem.attrib.get('Производитель')
        list_dates.append(elem.attrib.get('Производитель'))
        #number = elem.attrib.get('Номер')
        list_dates.append(elem.attrib.get('Номер'))
        #side = elem.attrib.get('L - R')
        list_dates.append(elem.attrib.get('L - R'))
        #front_back = elem.attrib.get('F - R')
        list_dates.append(elem.attrib.get('F - R'))
        #amount = elem.attrib.get('Количество')
        list_dates.append(elem.attrib.get('Количество'))
        #price = elem.attrib.get('Цена')
        list_dates.append(elem.attrib.get('Цена'))
        #availability = elem.attrib.get('Наличие')
        list_dates.append(elem.attrib.get('Наличие'))
        #direction = elem.attrib.get('Описание')
        list_dates.append(elem.attrib.get('Описание'))
        #new = elem.attrib.get('Новинка')
        list_dates.append(elem.attrib.get('Новинка'))
        #name_internet = elem.attrib.get('НаименованиеИнтернет')
        list_dates.append(elem.attrib.get('НаименованиеИнтернет'))
        #up_down = elem.attrib.get('ВерхНиз')
        list_dates.append(elem.attrib.get('ВерхНиз'))
        #transmission = elem.attrib.get('КПП')
        list_dates.append(elem.attrib.get('КПП'))
        #drive = elem.attrib.get('WD')
        list_dates.append(elem.attrib.get('WD'))
        #type_body = elem.attrib.get('ВидКузова')
        list_dates.append(elem.attrib.get('ВидКузова'))
        #synonim = elem.attrib.get('Синоним')
        list_dates.append(elem.attrib.get('Синоним'))
        #print(f"{id_in_1c}|{name}|{tab}|{brand}|{model}|{body}|{years}|{engine}|{state}|{producer}|{number}|{side}|{front_back}|{amount}|{price}|{availability}|{direction}|{new}|{name_internet}|{up_down}|{transmission}|{drive}|{type_body}|{synonim}")
        if searchelemindatabase(id_in_1c) == True:
            #print("Необходимо сделать UPDATE")
            updateindatabaserow(connection, cursor, list_dates)
        else:

            print("Необходимо сделать INSERT")
            print(list_dates)
            insertintodatabasenewrow(connection, cursor, list_dates)

    endtime = datetime.datetime.now()
    leadtime = datetime.datetime.now() - starttime

    return {"startfunction": starttime.strftime("%H:%M:%S"),
            "endtime": endtime.strftime("%H:%M:%S"),
            "leadtime": leadtime.total_seconds(),
            "result": "Данные обновлены"}


# Ручка для формирования прайс-листа Дром
@database.post("/createxmlfiledrom",
               summary="Формируем прайс листы для Дрома",
               description="Формируются два файла: Прайс лист в наличии : dromoutputinstock.xml; прайс лист под заказ: dromoutputonrequest.xml")
def createxmlfiledrom():

    # Получаем данные из БД
    dates = selectalldatesfromdatabase()

    # Создаём документ
    root = ET.Element('offers', date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M"))
    root2 = ET.Element('offers', date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M"))
    tree = ET.ElementTree(root)
    tree2 = ET.ElementTree(root2)
    for element in tqdm.tqdm(dates):
        if checkavailability(element) is True:
            insertdatesinxmldrom(root, element)
        else:
            insertdatesinxmldrom(root2, element)

    # Записываем данные в файл которые в наличии
    with open('exportfiles/drom/dromoutputinstock.xml', 'wb') as file:
        tree.write(file, encoding='UTF-8', xml_declaration=True)
    with open(pathsfiles.pathtodrom, 'wb') as file:
        tree.write(file, encoding='UTF-8', xml_declaration=True)

    # Записываем данные в файл которые под заказ
    with open('exportfiles/drom/dromoutputonrequest.xml', 'wb') as file:
        tree2.write(file, encoding='UTF-8', xml_declaration=True)
    with open(pathsfiles.drominrequest, 'wb') as file:
        tree2.write(file, encoding='UTF-8', xml_declaration=True)
    print("Формирование файлов завершено")

    return {
         "result": "Файл успешно создан"}


# Ручка для формирования прайс-листа Авито
@database.post("/createxmlfileavito",
               summary="Формируем прайс лист для Авито",
               description="Формируются файл: avitooutputinstock.xml")
def createxmlfileavito():

    # Получаем данные из БД
    dates = selectalldatesfromdatabase()

    # Создаём документ
    root = ET.Element('Ads', formatVersion="3", target="Avito.ru",
                      date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M"))
    tree = ET.ElementTree(root)
    for element in tqdm.tqdm(dates):
        if checkavailability(element) is True and checkproductname(element) is True:
            insertdatesinxmlavito(root, element)

    # Записываем данные в файл которые в наличии
    with open('exportfiles/avito/avitooutputinstock.xml', 'wb') as file:
        tree.write(file, encoding='UTF-8', xml_declaration=True)
    with open(pathsfiles.pathtoavito, 'wb') as file:
        tree.write(file, encoding='UTF-8', xml_declaration=True)

    return {
         "result": "Файл успешно создан"}


# Ручка для формирования прайс-листа 2gis
@database.post("/createymlfiledoublegis",
               summary="Формируем прайс лист для 2гис",
               description="Формируются файл: 2gis.yml")
def createymlfiledoublegis():
    # Получаем данные из базы
    dates = selectalldatesfromdatabase()

    # Создаём документ
    root = etree.Element('yml_catalog',
                         date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M"))
    tree = etree.ElementTree(root)

    # Добавляем заголовочные данные в файл
    offers = indertdefautdatesin2gis(root)
    for element in tqdm.tqdm(dates):
        if checkavailability(element) is True and checkproductname(element) is True:
            insertdatesin2gis(offers, element)

    # Записываем данные в файл которые в наличии
    with open('exportfiles/2gis/2gis.yml', 'wb') as file:
        tree.write(file, encoding='UTF-8', xml_declaration=True,
                   doctype='<!DOCTYPE yml_catalog SYSTEM "shops.dtd">')
    with open(pathsfiles.pathdoublegis, 'wb') as file:
        tree.write(file, encoding='UTF-8', xml_declaration=True,
                   doctype='<!DOCTYPE yml_catalog SYSTEM "shops.dtd">')

    return {
         "result": "Файл успешно создан"}


# Ручка для формирования прайс-листа VK
@database.post("/createymlfilevk",
               summary="Формируем прайс лист для группы VK",
               description="Формируются файл: vk.xml")
def createymlfilevk():
    # Получаем данные из базы
    dates = selectalldatesfromdatabase()

    # Создаём документ
    root = etree.Element('yml_catalog',
                         date=datetime.datetime.today().strftime(
                             "%Y-%m-%d %H:%M"))
    tree = etree.ElementTree(root)

    # Добавляем заголовочные данные в файл
    offers = indertdefautdatesinvk(root)
    for element in tqdm.tqdm(dates):
        if checkavailability(element) is True and checkproductname(element) is True:
            insertdatesinvk(offers, element)

    # Записываем данные в файл которые в наличии
    with open('exportfiles/vk/vk_.xml', 'wb') as file:
        tree.write(file, encoding='UTF-8', xml_declaration=True)

    return {
        "result": "Файл успешно создан"}