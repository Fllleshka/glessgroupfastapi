# Библиотека работы с датой и временем
import datetime
# Библиотека работы с файлами
import os

# Функция получения последней модификации файла
def getlastmodifieddate(file_path):
    try:
        timestamp = os.stat(file_path).st_mtime
        return datetime.datetime.fromtimestamp(timestamp)
    except FileNotFoundError:
        return None

# Функция принятия решения
def decisionmaking(pathfile, lasttimeupdate):
    # Получаем сегодняшнюю дату
    today = datetime.datetime.today()
    # Максимальное время без обновления
    oneday = datetime.timedelta(days=1)
    # Разница между датой сегодня и последнего изменения файла
    difference = today - lasttimeupdate
    # Обновление файла требуется
    if difference > oneday:
        return True
    # Обновление файла не требуется
    else:
        return False