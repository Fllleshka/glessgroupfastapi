# Библиотека работы с Google Sheets
import time
# Библиотека для работы с файлами
import gspread
# Библиотека для работы со временем
import datetime
# Импорт библиотеки для работы с TelegramBot
import telebot
# Библиотека для работы с HTTP запросами
import requests
# Библиотека для проверки кто создал файл
import win32security
# Импорт данных для работы
from dates import googlesheets, allsotr, beeline, colorsforbuttons, telegrambot

class class_logging_info_in_GoogleSheet:

    def __init__(self):
        # Подключаемся к сервисному аккаунту
        self.gc = gspread.service_account(googlesheets.CREDENTIALS_FILE)
        # Подключаемся к таблице по ключу таблицы
        self.table = self.gc.open_by_key(googlesheets.sheetkey)
        # Открываем лист LogsCallCenter
        self.worksheetlogs = self.table.worksheet("LogsCallCenter")
        # Открываем лист LogsPhotos
        self.worksheetlogsphotos = self.table.worksheet("LogsPhotos")
        # Получаем номер самой последней строки
        self.newstr = len(self.worksheetlogs.col_values(1)) + 1
        # Вычисляем номер строки
        self.newnumber = self.newstr - 1

    # Функция записи логирования изменения файла в таблицу Google
    def logging_updatedate_file_excel(self, filename):
        try:
            # Определяем время выполнения операции
            today = datetime.datetime.today().strftime("%d.%m.%Y | %H:%M:%S")
            # Определяем диапазон для объединения ячеек
            mergerange = "C" + str(self.newstr) + ":F" + str(self.newstr)
            # Объединяем ячейки да записи
            self.worksheetlogs.merge_cells(mergerange)
            # Добавляем запись в таблицу логирования
            self.worksheetlogs.update_cell(self.newstr, 1, self.newnumber)
            self.worksheetlogs.update_cell(self.newstr, 2, today)
            text = "Файл [" + filename + "] обновлён"
            self.worksheetlogs.update_cell(self.newstr, 3, text)
            # Окрашивание ячейки
            color = {"backgroundColor": {"red": 0.94, "green": 0.9,
                                         "blue": 0.15},
                     "horizontalAlignment": "CENTER"}
            self.worksheetlogs.format("C" + str(self.newstr), color)
            # Делаем центрирование ячейки
            self.worksheetlogs.format(mergerange, {"horizontalAlignment": "CENTER"})
        except Exception as e:
            print(f"Логирование call-центра сломалось: {e}")
            time.sleep(5)
            self.logging_updatedate_file_excel(filename)

    # Функция записи логов изменения Call Center
    def logging_update_call_center(self):
        try:
            # Определяем время выполнения операции
            today = datetime.datetime.today().strftime("%d.%m.%Y | %H:%M:%S")
            # Выясняем данные кто работает
            managerslist = []
            # Выясняем статусы менеджеров
            for element in allsotr.numbermanagers:
                # Запрос статуса во внешнем API
                urlforapi = beeline.urlapi + element + '/agent'
                status = requests.get(urlforapi,
                                      headers=beeline.headers).text
                # Добавление статуса в массив статусов
                managerslist.append(status)

            # Проверяем изменится ли call центр
            dates = self.worksheetlogs.row_values(self.newnumber)
            # Если данные уже сегодня записывались, то не дублируем их
            if dates[2] == managerslist[0] and dates[3] == managerslist[
                1] and dates[4] == managerslist[2] and dates[
                5] == managerslist[3] and str(dates[1])[:10] == str(today)[
                                                                :10]:
                pass
            # Если же эти данные не были записаны, записываем
            else:
                # Добавляем строку в конец файла логирования
                self.worksheetlogs.update_cell(self.newstr, 1, self.newnumber)
                self.worksheetlogs.update_cell(self.newstr, 2, today)

                for element in range(0, 4):
                    if managerslist[element] == '"ONLINE"' or managerslist[element] == '"OFFLINE"':
                        self.worksheetlogs.update_cell(self.newstr, element + 3, managerslist[element])
                    else:
                        self.worksheetlogs.update_cell(self.newstr, element + 3,"Ошибка данных")

                if managerslist[0] == '"ONLINE"':
                    self.worksheetlogs.format("C" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheetlogs.format("C" + str(self.newstr), colorsforbuttons.redcolor)

                if managerslist[1] == '"ONLINE"':
                    self.worksheetlogs.format("D" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheetlogs.format("D" + str(self.newstr), colorsforbuttons.redcolor)
                if managerslist[2] == '"ONLINE"':
                    self.worksheetlogs.format("E" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheetlogs.format("E" + str(self.newstr), colorsforbuttons.redcolor)
                if managerslist[3] == '"ONLINE"':
                    self.worksheetlogs.format("F" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheetlogs.format("F" + str(self.newstr), colorsforbuttons.redcolor)
                # Чтобы программа не падала из-за лимита количества запросов ставим sleep
                time.sleep(60)

        except Exception as e:
            print(f"Логирование call-центра сломалось: {e}")
            time.sleep(10)
            self.logging_update_call_center()

    # Функция выяснения данных о фотографии
    def select_dates_from_photo(self, path):
        sd = win32security.GetFileSecurity(path,win32security.OWNER_SECURITY_INFORMATION)
        owner_sid = sd.GetSecurityDescriptorOwner()
        match(str(owner_sid)):
            case allsotr.fleysner.idinwindows:
                return {'fio': allsotr.fleysner.shortname,
                        'cell_in_table': allsotr.fleysner.dateforsheets}
            case allsotr.kireev.idinwindows:
                return {'fio': allsotr.kireev.shortname,
                        'cell_in_table': allsotr.kireev.dateforsheets}
            case allsotr.pushcar.idinwindows:
                return {'fio': allsotr.pushcar.shortname,
                        'cell_in_table': allsotr.pushcar.dateforsheets}
            case allsotr.ivanov.idinwindows:
                return {'fio': allsotr.ivanov.shortname,
                        'cell_in_table': allsotr.ivanov.dateforsheets}
            case _:
                return {'fio': allsotr.noneuser.shortname,
                        'cell_in_table': allsotr.noneuser.dateforsheets}

    # Функция записи данных в Google Sheets
    def logging_dates_from_photo(self, dates):
        try:
            #  Получение данных из ячейки
            olddatefromcell = self.worksheetlogsphotos.get_values(dates.get('cell_in_table'))
            olddate = int(olddatefromcell[0][0])
            newdate = olddate + 1
            self.worksheetlogsphotos.update_acell(dates.get('cell_in_table'), newdate)
            return True
        except Exception:
            return Exception

    # Вставка данных в таблицу
    def insertdates2(self, cell):
        try:
            # Получаем данные
            value = self.worksheetlogsphotos.get_values(cell)
            if not value[0]:
                newvalue = 1
            else:
                newvalue = int(value[0][0]) + 1
            self.worksheetlogsphotos.update_acell(cell, newvalue)
            self.worksheetlogsphotos.format(cell, colorsforbuttons.borders)
            return True
        except Exception:
            return False

    # Функция записи данных внизу в Google Sheets
    def logging_dates_from_photo2(self, dates):
        try:
            # Получение числа сегодня
            # Определяем время выполнения операции
            today = datetime.datetime.today().strftime("%d.%m.%Y")
            # Получаем последнюю ячейку в столбце F
            laststrF = len(self.worksheetlogsphotos.col_values(6))
            lastvalue = self.worksheetlogsphotos.get('F' + str(laststrF))
            # Если за сегодня есть данные, добавляем
            if today == str(lastvalue[0][0]):
                # Выбираем нужную ячейку
                match dates['fio']:
                    case allsotr.fleysner.shortname:
                        cell = 'G' + str(laststrF)
                        # Записываем данные в ячейку
                        self.insertdates2(cell)
                        return True
                    case allsotr.ivanov.shortname:
                        cell = 'J' + str(laststrF)
                        # Записываем данные в ячейку
                        self.insertdates2(cell)
                        return True
                    case allsotr.kireev.shortname:
                        cell = 'H' + str(laststrF)
                        # Записываем данные в ячейку
                        self.insertdates2(cell)
                        return True
                    case allsotr.pushcar.shortname:
                        cell = 'I' + str(laststrF)
                        # Записываем данные в ячейку
                        self.insertdates2(cell)
                        return True
                    case _:
                        return False
            # Создаём новую строку
            else:
                newstr = laststrF + 1
                self.worksheetlogsphotos.update_cell(newstr, 6, today)
                # Окантовка ячеек
                for elem in ['F', 'G', 'H', 'I', 'J']:
                    cell = elem + str(newstr)
                    self.worksheetlogsphotos.format(cell, colorsforbuttons.borders)
                self.logging_dates_from_photo2(dates)
                return True
        except Exception:
            return Exception

# Класс оповещения в телеграмм боте
class send_message_telegram_bot:
    # Инициализация класса
    def __init__(self):
        self.botkey = telegrambot.botkey

    # Функция оповещения о балансе
    def notificationavito(self, textmessage):
        # Токен для связи с ботом
        bot = telebot.TeleBot(self.botkey)
        bot.send_message(allsotr.administrator.idintelegram, text=textmessage)
        bot.send_message(allsotr.sekachev.idintelegram, text=textmessage)

# Класс отправки сообщений c ошибками от телеграмм бота
class class_send_erorr_message(object):
    # Инициализация класса
    def __init__(self, argument, text, exception):
        self.time = argument
        self.function = text
        self.exception = exception
        self.botkey = telegrambot.botkey

    # Функция отправки сообщения об ошибке в работе функции администратору, системному администратору
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