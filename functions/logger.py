# Библиотека работы с Google Sheets
import time
# Библиотека для работы с файлами
import gspread
# Библиотека для работы со временем
import datetime
# Импорт данных для работы
from dates import googlesheets, allsotr, beeline, colorsforbuttons
# Импорт библиотеки для работы с TelegramBot
import telebot
# Библиотека для работы с HTTP запросами
import requests

# Функция записи логирования изменения файла в таблицу Google
def logging_updatedate_file_excel(filename):
    try:
        # Подключаемся к сервисному аккаунту
        gc = gspread.service_account(googlesheets.CREDENTIALS_FILE)
        # Подключаемся к таблице по ключу таблицы
        table = gc.open_by_key(googlesheets.sheetkey)
        # Открываем нужный лист
        worksheet = table.worksheet("LogsCallCenter")
        # Получаем номер самой последней строки
        newstr = len(worksheet.col_values(1)) + 1
        # Вычисляем номер строки
        newnumber = newstr - 1
        # Определяем время выполнения операции
        today = datetime.datetime.today().strftime("%d.%m.%Y | %H:%M:%S")
        # Определяем диапазон для обьединения ячеек
        mergerange = "C" + str(newstr) + ":F" + str(newstr)
        # Обьединяем ячейки да записи
        worksheet.merge_cells(mergerange)
        # Добавляем запись в таблицу логгирования
        worksheet.update_cell(newstr, 1, newnumber)
        worksheet.update_cell(newstr, 2, today)
        text = "Файл [" + filename + "] обновлён"
        worksheet.update_cell(newstr, 3, text)
        # Окрашивание ячейки
        color = {"backgroundColor": {"red": 0.94, "green": 0.9, "blue": 0.15},
                 "horizontalAlignment": "CENTER"}
        worksheet.format("C" + str(newstr), color)
        # Делаем центрирование ячейки
        worksheet.format(mergerange, {"horizontalAlignment": "CENTER"})
    except Exception as e:
        print(f"Логгирование call-центра сломалось: {e}")
        time.sleep(5)
        logging_updatedate_file_excel()

# Функция записи логов изменения Call Center
def logging_update_call_center():
    try:
        # Подключаемся к сервисному аккаунту
        gc = gspread.service_account(googlesheets.CREDENTIALS_FILE)
        # Подключаемся к таблице по ключу таблицы
        table = gc.open_by_key(googlesheets.sheetkey)
        # Открываем нужный лист
        worksheet = table.worksheet("LogsCallCenter")
        # Получаем номер самой последней строки
        newstr = len(worksheet.col_values(1)) + 1
        # Вычисляем номер строки
        newnumber = newstr - 1
        # Определяем время выполения операции
        today = datetime.datetime.today().strftime("%d.%m.%Y | %H:%M:%S")
        # Выясняем данные кто работает
        managerslist = []
        # Выясняем статусы менеджеров
        for element in allsotr.numbermanagers:
            # Запрос статуса во внешнем API
            urlforapi = beeline.urlapi + element + '/agent'
            status = requests.get(urlforapi, headers = beeline.headers).text
            # Добавление статуса в массив статусов
            managerslist.append(status)

        # Проверяем изменится ли call центр
        dates = worksheet.row_values(newnumber)
        # Если данные уже сегодня записывались, то не дублируем их
        if dates[2] == managerslist[0] and dates[3] == managerslist[1] and dates[4] == managerslist[2] and dates[
            5] == managerslist[3] and str(dates[1])[:10] == str(today)[:10]:
            pass
        # Если же эти данные не были записаны, записываем
        else:
            # Добавляем строку в конец файла логирования
            worksheet.update_cell(newstr, 1, newnumber)
            worksheet.update_cell(newstr, 2, today)

            for element in range(0, 4):
                if managerslist[element] == '"ONLINE"' or managerslist[element] == '"OFFLINE"':
                    worksheet.update_cell(newstr, element + 3, managerslist[element])
                else:
                    worksheet.update_cell(newstr, element + 3, "Ошибка данных")

            if managerslist[0] == '"ONLINE"':
                worksheet.format("C" + str(newstr), colorsforbuttons.greencolor)
            else:
                worksheet.format("C" + str(newstr), colorsforbuttons.redcolor)

            if managerslist[1] == '"ONLINE"':
                worksheet.format("D" + str(newstr), colorsforbuttons.greencolor)
            else:
                worksheet.format("D" + str(newstr), colorsforbuttons.redcolor)
            if managerslist[2] == '"ONLINE"':
                worksheet.format("E" + str(newstr), colorsforbuttons.greencolor)
            else:
                worksheet.format("E" + str(newstr), colorsforbuttons.redcolor)
            if managerslist[3] == '"ONLINE"':
                worksheet.format("F" + str(newstr), colorsforbuttons.greencolor)
            else:
                worksheet.format("F" + str(newstr), colorsforbuttons.redcolor)
            # Чтобы программа не падала из-за лимита количества запросов ставим sleep
            time.sleep(60)

    except Exception as e:
        print(f"Логирование call-центра сломалось: {e}")
        time.sleep(10)
        logging_update_call_center()

# Класс отправки сообщений от телеграмм бота
class class_send_erorr_message(object):
    # Инициализация класса
    def __init__(self, argument, text, exception, botkey):
        self.time = argument
        self.function = text
        self.exception = exception
        self.botkey = botkey

    # Функция отправки сообщения об ошибке администратору, системному администратору
    def send_message(self):
        # Формирование сообщения
        message = f"Возникла проблема с функцией:\n{str(self.function)}\n\n[{str(self.time)}]\nОшибка типа:\n[{str(self.exception)}]"
        # Токен для связи с ботом
        bot = telebot.TeleBot(self.botkey)
        # Отравляем сообщение на рабочий телефон администратора
        bot.send_message(1871580124,text=message)
        # Отравляем сообщение на личный телефон системного администратора
        bot.send_message(1917167694, text=message)
        return message