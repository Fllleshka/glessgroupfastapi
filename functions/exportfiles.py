# Импорт библиотеки для создания файлов xml
import xml.etree.ElementTree as ET
# Импорт класса для фраз к прайс-листам
from dates import textforpricelists, pathsfiles

# Импорт библиотеки для работы с файлами
import os
from lxml import etree
import tqdm

# Функция добавления данных в файл Дрома
def insertdatesinxmldrom(root, element):
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

# Функция добавления данных в файл Авито
def insertdatesinxmlavito(root, element):
    # Добавляем дочерный элемент
    offer = ET.SubElement(root, "Ad")
    # Номер в 1С
    addstr(offer, "Id", element[1])
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Статус
    addstr(offer, "AdStatus", "Free")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Метод связи
    addstr(offer, "ContactMethod", "По телефону и в сообщениях")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Имя менеджера
    addstr(offer, "ManagerName", "Владислав")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Номер телефона
    addstr(offer, "ContactPhone", "+79059402069")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Адрес
    addstr(offer, "Address",
                "Россия, Омская область, Омск, улица Лизы Чайкина, 7к3")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Категория
    addstr(offer, "Category", "Запчасти и аксессуары")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Подкатегория 1
    # self.addstr(offer, "GoodsType", "Запчасти")
    addstr(offer, "GoodsType", goodstype(element[2]))

    # print("\tarticle\t", element[1], "\t\t\t", )

    # Подкатегория 2
    addstr(offer, "ProductType", producttype(element[2]))
    # print("\tarticle\t", element[1], "\t\t\t", )

    # AdType
    addstr(offer, "AdType", "Товар приобретен на продажу")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # SparePartType
    addstr(offer, "SparePartType", "Трансмиссия и привод")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # TransmissionSparePartType
    addstr(offer, "TransmissionSparePartType", "КПП в сборе")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # EngineSparePartType
    addstr(offer, "EngineSparePartType", "Блок цилиндров, головка, картер")
    # print("\tarticle\t", element[1], "\t\t\t", )

    # Название товара в 1С
    addstr(offer, "Title", element[2])
    # print("\tname\t", element[2])

    # Состояние новый или б/у
    addstr(offer, "Condition", selectcondition(element[9]))
    # print("\tstate\t", self.selectcondition(element[9]))

    # Цена
    addstr(offer, "Price", element[15])
    # print("\tprice\t", element[15])

    # Фотографии
    textphoto = createtextsphotos(element[1])
    addstr(offer, "Images", textphoto)

    # Наличие
    addstr(offer, "Availability", element[16])
    # print("\tprice\t", element[15])

    # Каталожный номер запчасти
    addstr(offer, "OEM", changeOEM(element[11]))
    # print("\tnumber\t", element[11])

    # Марка производителя
    addstr(offer, "Brand", selectmake(element[10]))
    # print("\tПроизводитель\t", self.selectmake(element[10]))

    # Описание
    newdescription = textforpricelists.initialphrase
    if element[10] == "Капремонт" or element[10] == "Переборка":
        newdescription += textforpricelists.majorrenovation
    elif element[10] == "Китай" or element[10] == "Тайвань":
        newdescription += textforpricelists.madeinсhina
    elif element[10] == "Россия":
        newdescription += textforpricelists.madeinrussia
    elif element[10] == "Прокачана":
        newdescription += textforpricelists.madeingless
    else:
        if len(element[17]) == 0:
            newdescription += textforpricelists.middlerase
        else:
            newdescription += str(element[17])
    newdescription += textforpricelists.endphrase
    addstr(offer, "Description", newdescription)
    # print("\tdirection\t", element[17])

# Функция добавления данных в файл 2gis
def insertdatesin2gis(offers, element):

    # Создаём элемент
    offer = etree.SubElement(offers, 'offer', available="true")
    # Добавляем цену
    price = etree.SubElement(offer, 'price')
    price.text = str(element[3])
    # Добавляем название
    name = etree.SubElement(offer, 'name')
    name.text = element[2]
    # Добавляем фотографии
    picture = etree.SubElement(offer, 'picture')
    picture.text = "https://" + pathsfiles.pathsitefolder + "1/" + str(element[0]) + ".jpg"
    # Добавляем categoryid
    categoryId = etree.SubElement(offer, 'categoryId')
    categoryId.text = "1"
    # Добавляем описание
    description = etree.SubElement(offer, 'description')

    if element[17] == "":
        descriptiontext = (textforpricelists.initialphrase2gis +
                           textforpricelists.middlerase2gis +
                           textforpricelists.endphrase)
    else:
        descriptiontext = (textforpricelists.initialphrase2gis +
                           str(element[17]) +
                           textforpricelists.endphrase)
    description.text = descriptiontext

# Функция добавления данных в файл VK
def insertdatesinvk(offers, element):
    # Создаём элемент
    offer = etree.SubElement(offers, 'offer', available="true", id=str(element[1]), group_id = "1")
    # Добавляем цену
    price = etree.SubElement(offer, 'price')
    price.text = str(element[3])
    # Добавляем валюту
    currency = etree.SubElement(offer, 'currencyId')
    currency.text = 'RUB'
    # Добавляем idCategory
    idcategory = etree.SubElement(offer, 'categoryId')
    idcategory.text = "1"
    # Добавляем название запчасти
    name = etree.SubElement(offer, 'name')
    name.text = element[2]
    # Добавляем количество товара
    count = etree.SubElement(offer, 'count')
    count.text = "1"
    # Добавляем фотографии
    picture = etree.SubElement(offer, 'picture')
    picture.text = "https://" + pathsfiles.pathsitefolder + "1/" + str(
        element[1]) + ".jpg"
    # Добавляем описание
    description = etree.SubElement(offer, 'description')

    if element[17] == "":
        descriptiontext = "Описание пока не добавлено"
    else:
        descriptiontext = element[17]

    description.text = descriptiontext

# Добавляем заголовочных данные в файл 2gis
def indertdefautdatesin2gis(root):
    shop = etree.SubElement(root, 'shop')
    name = etree.SubElement(shop, 'name')
    name.text = "Gless Group"
    company = etree.SubElement(shop, 'company')
    company.text = "Gless Group"
    categories = etree.SubElement(shop, 'categories')
    category = etree.SubElement(categories, 'categories', id="1")
    category.text = "Автозапчасти"
    offers = etree.SubElement(shop, 'offers')
    return offers

# Добавляем заголовочных данные в файл VK
def indertdefautdatesinvk(root):
    shop = etree.SubElement(root, 'shop')
    name = etree.SubElement(shop, 'name')
    name.text = "Gless Group"
    company = etree.SubElement(shop, 'company')
    company.text = "Gless Group"
    url = etree.SubElement(shop, 'url')
    url.text = "https://gless.group/"
    currencies = etree.SubElement(shop, 'currencies')
    currency = etree.SubElement(currencies, 'currency', id='RUB', rate="1")

    categories = etree.SubElement(shop, 'categories')
    category = etree.SubElement(categories, 'category', id="1")
    category.text = "Автозапчасти"
    offers = etree.SubElement(shop, 'offers')
    return offers

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

# Функция обработки категории для Авито
def goodstype(name_in_1C):
    if name_in_1C.find("Масло для АКПП") == 0:
        return "Масла и автохимия"

    return "Запчасти"

# Функция подкатегорий для Авито
def producttype(name_in_1C):
    if name_in_1C.find("Масло для АКПП") == 0:
        return "Моторные масла"
    if name_in_1C.find("Антифриз") == 0:
        return "Охлаждающие жидкости"
    else:
        return "Для автомобилей"

# Функция корректировки номера каталожного для Авито
def changeOEM(number):
    oldnumber2 = number
    # Обработка квитанции комитента
    if "кв" in number:
        # Позиция 'кв'
        positionstart = number.find("кв") - 1
        # Новая строка
        newnuber = number[:positionstart]

        # Если запятая присутствует
        if "," in newnuber:
            newnuber = newnuber[:-1]
        else:
            pass
        number = newnuber

    # Обработка позиций втулок регулировочных
    if "L=" in number:
        # Позиция ', L='
        positionstart = number.find("L=") - 1
        # Новая строка
        newnumber = number[:positionstart]
        number = newnumber

    replacements = {
        # Запятые
        ",": " ",
        # Скобочки
        "(": "-",
        ")": "-",
        # Хэштег
        "#": "-",
        # Плюс
        "+": "-",
        # Вопросы
        "?": "0",
        # Двоеточие
        ":": " ",
        "*": "0",
    }

    for old, new in replacements.items():
        number = number.replace(old, new)
    return number

# Функция формирования состояния детали для Авито
def selectcondition(element):
    match(element):
        case "Новый":
            return "Новое"
        case "Б/У" | "Квитанция комитента":
            return "Б/у"
    return element

# Функция формирования правильного производителя для Авито
def selectmake(element):
    match(element):
        case "Контракт" | "<>" | "Капремонт" | "Китай" | "Тайвань" | "Переборка" | "ХЗ" | "Россия" | "Прокачана" | "Ручная работа" | "ЗОН" | "V&V" | "ALLRING":
            return "Mazda"
        case "NEEDFUL" | "NO NAME":
            return "Россдеталь"
        case "DYNAMATRIX-KOREA":
            return "DYNAMATRIX"
        case "Тосол-Синтез":
            return "ТОСОЛСИНТЕЗ"
        case "Seinsa":
            return "Seinsa Autofren"
        case "MITSUBISHI ELECTRIC":
            return "MITSUBISHIELECTRIC"
        case "Maruichi":
            return "1-56 (Maruichi)"
        case "STELLOX":
            return "Stellox"
        case "АРЗ":
            return "Пороги-Авто"
        case "ТУРБО Инженерик":
            return "TURBOENGINEERING"
        case "Lian Touh":
            return "LIANTUOH"
        case "LUTAS":
            return "Japanparts"
        case "ABAPrime":
            return "ABA"
        case "ВМП Авто":
            return "ВМПАВТО"
        case "SPACO":
            return "SPACODIESEL"
        case "Country":
            return "Delfin Group"
        case "Wynn’s":
            return "Wynns"
        case "Superautofix":
            return "SuperATV"
        case "MITSU":
            return "MITSUBISHI HEAVY INDUSTRIES"
        case "EP":
            return "EVERPOWER"
        case _:
            return element

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

# Функция преобразования данных
def transformationdata(dates):
    outputdates = []
    for element in dates:
        if element[1] == "В наличии":
            outputdates.append(element)
        else:
            continue
    return outputdates