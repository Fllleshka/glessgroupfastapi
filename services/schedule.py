# Библиотека для работы с бинарниками
import io
import zipfile
import logging
# Библиотека для работы с файлами excel
import openpyxl
# Библиотека для открывания запароленных файлов
import msoffcrypto

from msoffcrypto.exceptions import FileFormatError, InvalidKeyError, DecryptionError
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils.exceptions import InvalidFileException
from pathlib import PureWindowsPath
from config import get_settings
from services.smb import read_smb_file, SmbFileNotFoundError, SmbUnavailableError

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

# Чтение файла
def read_schedule_bytes(year: int) -> bytes:
    # Импорт настроек
    settings = get_settings()
    # Составляем путь до файла
    full_path_to_file = str(PureWindowsPath(settings.schedule_folder) / schedule_filename(year))

    try:
        return read_smb_file(full_path_to_file)
    except SmbFileNotFoundError as e:
        raise ScheduleNotFoundError(f"Файл графика на {year} год не найден") from e
    except SmbUnavailableError as e:
        raise ScheduleUnavailableError("Сетевой диск с графиком недоступен") from e

# Сборка всего модуля в функцию
def load_month_schedule(year: int, month: int) -> dict[str, list[str]]:
    data = read_schedule_bytes(year)
    password = get_settings().schedule_password.get_secret_value()
    sheet = open_schedule(data, password)
    month_row = find_month_row(sheet, month)
    return read_month_schedule(sheet, month_row)