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
# Библиотека для проверки кто создал файл
import win32security

class class_logging_info_in_GoogleSheet:

    def __init__(self):
        # Подключаемся к сервисному аккаунту
        self.gc = gspread.service_account(googlesheets.CREDENTIALS_FILE)
        # Подключаемся к таблице по ключу таблицы
        self.table = self.gc.open_by_key(googlesheets.sheetkey)
        # Открываем нужный лист
        self.worksheet = self.table.worksheet("LogsCallCenter")
        # Получаем номер самой последней строки
        self.newstr = len(self.worksheet.col_values(1)) + 1
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
            self.worksheet.merge_cells(mergerange)
            # Добавляем запись в таблицу логирования
            self.worksheet.update_cell(self.newstr, 1, self.newnumber)
            self.worksheet.update_cell(self.newstr, 2, today)
            text = "Файл [" + filename + "] обновлён"
            self.worksheet.update_cell(self.newstr, 3, text)
            # Окрашивание ячейки
            color = {"backgroundColor": {"red": 0.94, "green": 0.9,
                                         "blue": 0.15},
                     "horizontalAlignment": "CENTER"}
            self.worksheet.format("C" + str(self.newstr), color)
            # Делаем центрирование ячейки
            self.worksheet.format(mergerange, {"horizontalAlignment": "CENTER"})
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
            dates = self.worksheet.row_values(self.newnumber)
            # Если данные уже сегодня записывались, то не дублируем их
            if dates[2] == managerslist[0] and dates[3] == managerslist[
                1] and dates[4] == managerslist[2] and dates[
                5] == managerslist[3] and str(dates[1])[:10] == str(today)[
                                                                :10]:
                pass
            # Если же эти данные не были записаны, записываем
            else:
                # Добавляем строку в конец файла логирования
                self.worksheet.update_cell(self.newstr, 1, self.newnumber)
                self.worksheet.update_cell(self.newstr, 2, today)

                for element in range(0, 4):
                    if managerslist[element] == '"ONLINE"' or managerslist[element] == '"OFFLINE"':
                        self.worksheet.update_cell(self.newstr, element + 3, managerslist[element])
                    else:
                        self.worksheet.update_cell(self.newstr, element + 3,"Ошибка данных")

                if managerslist[0] == '"ONLINE"':
                    self.worksheet.format("C" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheet.format("C" + str(self.newstr), colorsforbuttons.redcolor)

                if managerslist[1] == '"ONLINE"':
                    self.worksheet.format("D" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheet.format("D" + str(self.newstr), colorsforbuttons.redcolor)
                if managerslist[2] == '"ONLINE"':
                    self.worksheet.format("E" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheet.format("E" + str(self.newstr), colorsforbuttons.redcolor)
                if managerslist[3] == '"ONLINE"':
                    self.worksheet.format("F" + str(self.newstr), colorsforbuttons.greencolor)
                else:
                    self.worksheet.format("F" + str(self.newstr), colorsforbuttons.redcolor)
                # Чтобы программа не падала из-за лимита количества запросов ставим sleep
                time.sleep(60)

        except Exception as e:
            print(f"Логирование call-центра сломалось: {e}")
            time.sleep(10)
            self.logging_update_call_center()

    # Функция записи данных в Google Sheet файл logs
    def logging_folders_with_photos(self, path):

        sd = win32security.GetFileSecurity(path,win32security.OWNER_SECURITY_INFORMATION)
        owner_sid = sd.GetSecurityDescriptorOwner()
        print(f'Owner_SID: {owner_sid}')
        print(f'\t\t{allsotr.fleysner.idinwindows}')
        match(owner_sid):
            case allsotr.fleysner.idinwindows:
                return {'fio': allsotr.fleysner.shortname,
                        'cell_in_table': allsotr.fleysner.dateforsheets}
            case allsotr.kireev.idinwindows:
                return {}
            case allsotr.pushcar.idinwindows:
                return {}
            case allsotr.ivanov.idinwindows:
                return {}
            case _:
                return {}

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