# Библиотеки для работы с Excel
import os.path
# Библиотека для работы со временем
import datetime
# Библиотека для работы с данными о файлах
import openpyxl
# Библиотека для работы с файлами
import shutil
# Библиотека для работы с бинарниками
import io
# Библиотека для открывания запароленный файлов
import msoffcrypto

# Импорт данных из файла
from dates import datesforexcelfiles
# Импорт функций логирования
#from functions.logger import class_logging_info_in_GoogleSheet

# Функция открытия зашифрованного файла(или нет если нет пароля)
def readprotectedfile(path, password) -> io.BytesIO:
    # Получаем полный путь
    basedir = os.getcwd()
    filepath = basedir + "/" + path

    # Если файл зашифрован
    with open(filepath, "rb") as f:
        file = msoffcrypto.OfficeFile(f)
        if file.is_encrypted():
            if not password:
                raise ValueError("Файл защищён паролем, а пароль не указан")
            decrypted = io.BytesIO()
            file.load_key(password=password)
            file.decrypt(decrypted)
            decrypted.seek(0)
            return decrypted
    # Если файл не зашифрован читаем как есть
    with open(filepath, "rb") as f:
        return io.BytesIO(f.read())

# Функция записи полученных данных в новый файл
def writecopyfile(dates, path) -> None:
    with open(path, "wb") as outfile:
        outfile.write(dates.getbuffer())

# Функция копирования данный в файл для работы
def checkupdatedatesexcel() -> bool:
    # Вычисляем время последнего изменения основного документа
    file1 = openpyxl.load_workbook(datesforexcelfiles.pathmainfile).properties.modified
    # Вычисляем дату последнего изменения рабочего документа
    file2 = openpyxl.load_workbook(datesforexcelfiles.pathfile).properties.modified

    print(f"FILE1: {file1}")
    print(f"FILE2: {file2}")

    # Вычисляем разницу времён
    diff_times = file1 - file2

    print(f"DIFF: {diff_times}")
    # Устанавливаем максимальное время разницы файлов
    deltatime = datetime.timedelta(days = 0, hours = 0, minutes = 5)
    # Если deltatime меньше разницы во времени изменения файлов
    if deltatime < diff_times:
        # Выполняем копирование
        result = shutil.copy2(datesforexcelfiles.pathmainfile, datesforexcelfiles.pathfile, follow_symlinks = True)
        print(f"Результат выполнения копирования {result}")
        namefile = os.path.basename(datesforexcelfiles.pathfile)
        # Логирование обновления файла
        #classlog = class_logging_info_in_GoogleSheet()
        #classlog.logging_updatedate_file_excel(namefile)
        return True
    else:
        return False

# Функция импорта данных из файла для работы
def importdatesformexcel(path, password):

    # Экземпляр COM обьекта
    #xlApp = win32com.client.Dispatch("Excel.Application", pythoncom.CoInitialize())
    # Открываем файл
    #xlwb = xlApp.Workbooks.Open(path, False, True, None, password)
    wb = openpyxl.load_workbook(path)
    # Выбираем лист(таблицу)
    #sheet = xlwb.ActiveSheet
    sheet = wb.active
    # Выбираем данные из range
    alldates = sheet["B1:B451"]

    # Выясняем текущий месяц
    today = datetime.datetime.today()
    todayyear = int(today.strftime("%Y"))
    listmontheng = [datetime.date(todayyear, 1, 1).strftime("%B"),
                    datetime.date(todayyear, 2, 1).strftime("%B"),
                    datetime.date(todayyear, 3, 1).strftime("%B"),
                    datetime.date(todayyear, 4, 1).strftime("%B"),
                    datetime.date(todayyear, 5, 1).strftime("%B"),
                    datetime.date(todayyear, 6, 1).strftime("%B"),
                    datetime.date(todayyear, 7, 1).strftime("%B"),
                    datetime.date(todayyear, 8, 1).strftime("%B"),
                    datetime.date(todayyear, 9, 1).strftime("%B"),
                    datetime.date(todayyear, 10, 1).strftime("%B"),
                    datetime.date(todayyear, 11, 1).strftime("%B"),
                    datetime.date(todayyear, 12, 1).strftime("%B")]
    listmonthrus = ["ЯНВАРЬ", "ФЕВРАЛЬ", "МАРТ", "АПРЕЛЬ", "МАЙ", "ИЮНЬ",
                    "ИЮЛЬ", "АВГУСТ", "СЕНТЯБРЬ", "ОКТЯБРЬ",
                    "НОЯБРЬ", "ДЕКАБРЬ"]
    todaymontheng = today.strftime("%B")
    todaymonthrus = listmonthrus[listmontheng.index(todaymontheng)]

    # Ищем стартовую ячейку, для определения графика на этот месяц
    index = 0
    indexmonth = 0
    # Перебираем все элементы и находим нужную ячейку с текущим месяцем

    for row in alldates:
        index = index + 1
        for cell in row:
            if str(cell.value) == todaymonthrus:
                indexmonth = index

    # Формируем название ячейки начала импорта
    firstcell = "B" + str(indexmonth)
    # Формируем название ячейки конца импорта
    lastcell = "AG" + str(indexmonth + 31)
    # Формируем строку для импорта
    cellsrange = firstcell + ":" + lastcell
    # Импортируем данные за нужный нам месяц
    datesforsolution = sheet[cellsrange]

    # Формируем данные в список
    listdatesforsolution = []
    for row in datesforsolution:
        for element in row:
            listdatesforsolution.append(str(element.value))

    # Закрываем объект
    wb.close()

    # Возвращаем данные
    return listdatesforsolution

# Функция для выборки по данным
def chosedates(dates, allsotr):

    # Удаляем первый элемент
    del dates[0]

    # Считаем дни в месяце
    index = 0
    for element in dates:
        index = index + 1
        if element == "None" or element == "Торговля":
            # Определяем количество дней в месяце
            countdaysinmonth = index - 1
            break

    print("Данные до преобразования")
    for elem in dates:
        print(elem)

    # Удаляем ненужные данные
    #for element in dates:
    #    if element == allsotr.massmanagers_short[0]:
    #        print(allsotr.massmanagers_short[0])
    #        print(element)
    #        delelements = dates.index(element)
    #del dates[0:delelements]

    #print("Данные после преобразования")
    #for elem in dates:
    #    print(elem)

    return True
    '''
    # Разбиваем массив для конкретизации графика каждого менеджера
    managerlists = []
    #lenmanagers = len(massmanagers) - 1
    lenmanagers = len(allsotr.massmanagers_short) - 1
    for i in range(0, lenmanagers):
        managerlist = []
        index = 0
        for element in dates:
            managerlist.append(element)
            index += 1
            if index == 32:
                break
        managerlists.append(managerlist)
        del dates[0:32]

    # Выясняем график работы ПП
    deldates = 32 * 8
    # Удаляем ненужные данные
    del dates[0:deldates]
    # Добавляем в массив работников данные
    managerlist = []
    index = 0
    for element in dates:
        managerlist.append(element)
        index = index + 1
        if index == countdaysinmonth + 1:
            break
    managerlists.append(managerlist)
    return managerlists
    '''