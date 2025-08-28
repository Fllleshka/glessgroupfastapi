# Библиотеки для работы с Excel
import win32com.client
import pythoncom
# Библиотека для работы со временем
import datetime

# Функция импорта данных из файла для работы
def importdatesformexcel(path, password):
    # Экземпляр COM обьекта
    xlApp = win32com.client.Dispatch("Excel.Application", pythoncom.CoInitialize())
    # Открываем фаил
    xlwb = xlApp.Workbooks.Open(path, False, True, None, password)
    # Выбираем лист(таблицу)
    sheet = xlwb.ActiveSheet
    # Выбираем данные из range
    alldates = sheet.Range("B1:B451")

    # Выясняем текущий мясяц
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
    for element in alldates:
        index = index + 1
        if str(element) == todaymonthrus:
            indexmonth = index
    # Формируем название ячейки начала импорта
    firstcell = "B" + str(indexmonth)
    # Формируем название ячейки конца импорта
    lastcell = "AG" + str(indexmonth + 31)
    # Формируем строку для импорта
    cellsrange = firstcell + ":" + lastcell
    # Импортируем данные за нужный нам месяц
    datesforsolution = sheet.Range(cellsrange)
    # Формируем данные в список
    listdatesforsolution = []
    for element in datesforsolution:
        listdatesforsolution.append(str(element))
    # Закрываем фаил
    xlwb.Close()
    # Закрываем COM обьект
    xlApp.Quit()

    # Возвращаем данные
    return listdatesforsolution

# Функция для выбоки по данным
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

    # Удаляем ненужные данные
    for element in dates:
        #if element == massmanagers[0]:
        if element == allsotr.massmanagers_short[0]:
            delelements = dates.index(element)
    del dates[0:delelements]

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