# Библиотека для работы с бинарниками
import errno
import io
import time

# Библиотека для открывания запароленных файлов
import msoffcrypto
from msoffcrypto.exceptions import FileFormatError, InvalidKeyError, DecryptionError
# Библиотека для работы с файлами excel
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils.exceptions import InvalidFileException
import zipfile
# Библиотека для получения файла по smb
import smbclient

import logging
from pathlib import Path, PureWindowsPath

from smbprotocol.exceptions import SMBOSError

from config import get_settings

MONTHS_RU = ("ЯНВАРЬ",
             "ФЕВРАЛЬ",
             "МАРТ",
             "АПРЕЛЬ",
             "МАЙ",
             "ИЮНЬ",
             "ИЮЛЬ",
             "АВГУСТ",
             "СЕНТЯБРЬ",
             "ОКТЯБРЬ",
             "НОЯБРЬ",
             "ДЕКАБРЬ")
STOP_MARK = "ОБЩИЙ ИТОГ"
OFF_MARKS = {"В", "О", "O", "0", "X", "Х"}
NAME_COLUMN = 2
FIRST_DAY_COLUMN = 3
SMB_TIMEOUT = 10
READ_ATTEMPTS = 3
READ_DELAY = 3

# Объявление логгера
logger = logging.getLogger(__name__)

# Ошибка работы с графиком
class ScheduleError(Exception):
    """Общая ошибка работы с графиком."""

# Ошибка в графике нет нужного блока месяца
class MonthNotFoundError(ScheduleError):
    """В графике нет блока нужного месяца."""

# Ошибка пароль к файлу не указан
class ScheduleOpenError(ScheduleError):
    """Не удалось открыть файл графика."""

# Ошибка файл отсутствует в папке
class ScheduleNotFoundError(ScheduleError):
    """Файла графика на нужный год нет в папке."""

# Ошибка связанная с отсутствием доступа к файлу(пароль или путь)
class ScheduleUnavailableError(ScheduleError):
    """Не удалось прочитать файл графика: сетевой диск недоступен или неверные логин и пароль."""

# Нормализация имени
def normalize_name(name: object) -> str:
    if not isinstance(name, str):
        return ""
    # Обработка букв ё на е и Ё на Е
    name = name.replace("ё", "е").replace("Ё", "Е")
    # Убираем пробелы
    name = " ".join(name.split())
    return name.upper()

# Открытие файла и получение всех данных в память
def open_schedule(data: bytes, password: str | None) -> Worksheet:
    try:
        # Получаем файл
        buff = io.BytesIO(data)
        file = msoffcrypto.OfficeFile(buff)
        # Если файл зашифрован
        if file.is_encrypted():
            if not password:
                raise ScheduleOpenError("Файл защищён паролем, а пароль не указан")

            decrypted = io.BytesIO()
            file.load_key(password=password)
            file.decrypt(decrypted)
            buff = decrypted
        # Смещение файла в начало
        buff.seek(0)
        # Читаем нужную страницу
        workbook = openpyxl.load_workbook(buff, data_only=True)
        return workbook.active
    except (FileFormatError, InvalidKeyError, DecryptionError, InvalidFileException, zipfile.BadZipFile) as e:
        raise ScheduleOpenError("Не удалось открыть файл графика") from e

# Поиск номера строки с нужным месяцем в файле
def find_month_row(table, numbermonth: int) -> int:
    monthname = MONTHS_RU[numbermonth-1]
    for row in table.iter_rows(min_col = NAME_COLUMN, max_col = NAME_COLUMN):
        cell = row[0]
        if normalize_name(cell.value) == monthname:
            return cell.row
    raise MonthNotFoundError(f"В графике нет месяца {monthname}")

# Нормализация значения в ячейке
def normalize_mark(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()

# Читаем необходимые данные из таблицы
def read_month_schedule(table, month_row: int) -> dict[str, list[str]]:
    result = {}
    dates = table.iter_rows(min_row=month_row + 1, max_col=FIRST_DAY_COLUMN + 30, values_only=True)
    for row in dates:
        name = normalize_name(row[NAME_COLUMN - 1])
        if name in MONTHS_RU or name == STOP_MARK:
            break
        if name == "":
            continue
        result[name] = [normalize_mark(value) for value in row[FIRST_DAY_COLUMN - 1:]]
    return result

# Вычисление должен ли работать сегодня человек
def is_day_off(mark: str) -> bool:
    if mark in OFF_MARKS:
        return True
    return False

# Определение статуса на день
def status_for_day(schedule: dict, name: str, day: int) -> str | None:
    normalname = normalize_name(name)
    if normalname not in schedule:
        return None
    if is_day_off(schedule[normalname][day - 1]):
        return "OFFLINE"
    return "ONLINE"

# Составление актуального названия файла
def schedule_filename(year:int) -> str:
    return f"График OEM {year}.xlsx"

# Чтение файла excel
def read_schedule_bytes(year: int) -> bytes:
    # Импорт настроек
    settings = get_settings()
    # Составляем путь до файла
    full_path_to_file = str(PureWindowsPath(settings.schedule_folder) / schedule_filename(year))
    # Читаем данные
    for attempt in range(1, READ_ATTEMPTS + 1):
        try:
            with smbclient.open_file(full_path_to_file,
                                mode = "rb",
                                username = settings.smb_user,
                                password = settings.smb_password.get_secret_value(),
                                share_access = "rw",
                                connection_timeout = SMB_TIMEOUT) as file:
                return file.read()
        except SMBOSError as e:
            if e.errno == errno.ENOENT:
                raise ScheduleNotFoundError(f"Файла {schedule_filename(year)} нет в папке.") from e
            raise ScheduleUnavailableError("Сетевой диск недоступен или неверные логин и пароль") from e
        except ValueError as e:
            logger.warning(f"Предупреждение открытия файла {full_path_to_file} попытка {attempt} не удалась")
            if attempt != READ_ATTEMPTS:
                time.sleep(READ_DELAY)
            last_error = e
    raise ScheduleUnavailableError(f"Сетевой диск с графиком недоступен, попыток: {READ_ATTEMPTS}")from last_error