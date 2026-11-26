import io

import pytest
import openpyxl

from services.schedule import MONTHS_RU, NAME_COLUMN, ScheduleOpenError
from services.schedule import normalize_name
from services.schedule import find_month_row
from services.schedule import normalize_mark
from services.schedule import is_day_off
from services.schedule import read_month_schedule
from services.schedule import status_for_day
from services.schedule import open_schedule
from services.schedule import schedule_filename


# Подготавливаем для теста таблицу
@pytest.fixture
def sheet():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.cell(row=1, column=NAME_COLUMN, value="НОЯБРЬ")
    sheet.cell(row=2, column=NAME_COLUMN, value="Береговой Е.О.")
    sheet.cell(row=3, column=NAME_COLUMN, value="")
    sheet.cell(row=4, column=NAME_COLUMN, value="декабрь")
    sheet.cell(row=5, column=NAME_COLUMN, value="Береговой Е.О.")
    sheet.cell(row=6, column=NAME_COLUMN, value="Секачёв С.Ю.")
    sheet.cell(row=7, column=NAME_COLUMN, value="ОБЩИЙ ИТОГ")
    sheet.cell(row=8, column=NAME_COLUMN, value="Береговой Е.О.")
    sheet.cell(row=1, column=3, value=" ")
    sheet.cell(row=2, column=3, value="В")
    sheet.cell(row=2, column=4, value="9")
    sheet.cell(row=2, column=5, value=9)
    sheet.cell(row=3, column=3, value=" ")
    sheet.cell(row=4, column=3, value=" ")
    sheet.cell(row=5, column=3, value="9")
    sheet.cell(row=5, column=4, value="В")
    sheet.cell(row=5, column=5, value=9)
    sheet.cell(row=6, column=3, value="О")
    sheet.cell(row=6, column=4, value="Р")
    sheet.cell(row=6, column=5, value="10")
    sheet.cell(row=7, column=3, value=" ")
    sheet.cell(row=8, column=3, value="")

    return sheet

# Подготавливаем для теста список
@pytest.fixture
def schedule():
    return {
        "БЕРЕГОВОЙ Е.О.": ["9", "В", "9"],
        "СЕКАЧЕВ С.Ю.": ["О", "Р", "10"],
    }

# Тест нормализация имени
@pytest.mark.parametrize("name, expected",[(3, ""),
                                         (None, ""),
                                         (0.6, ""),
                                         ("Секачёв С.Ю.", "СЕКАЧЕВ С.Ю."),
                                         ("Ёжов  И.Ю.", "ЕЖОВ И.Ю."),
                                         ("  береговой е.о. ", "БЕРЕГОВОЙ Е.О.")])
def test_normalize_name(name: object, expected: str):
    assert normalize_name(name) == expected

# Тест поиска номера строки с нужным месяцем в файле
@pytest.mark.parametrize("numbermonth, expected",[(11, 1),
                         (12, 4)])
def test_find_month_row(sheet, numbermonth: int, expected: int):
    assert find_month_row(sheet, numbermonth) == expected


# Тест нормализация значения в ячейке
@pytest.mark.parametrize("value, expected",[(None, ""),
                                         (9, "9"),
                                         (" в ", "В"),
                                         ("Р", "Р")])
def test_normalize_mark(value: object, expected: str):
    assert normalize_mark(value) == expected


# Тест вычисление должен ли работать сегодня человек
@pytest.mark.parametrize("mark, expected",[("В", True),
                                         ("O", True),
                                         ("О", True),
                                         ("0", True),
                                         ("X", True),
                                         ("Х", True),
                                         ("9", False),
                                         ("10", False),
                                         ("Р", False),
                                         ("", False),])
def test_is_day_off(mark: str, expected: bool ):
    assert is_day_off(mark) == expected


# Тест чтения необходимые данные из таблицы
@pytest.mark.parametrize("month_row, name, expected", [
                        (1, "БЕРЕГОВОЙ Е.О.", ["В", "9", "9"]),
                        (4, "БЕРЕГОВОЙ Е.О.", ["9", "В", "9"]),
                        (4, "СЕКАЧЕВ С.Ю.", ["О", "Р", "10"]),])
def test_read_month_schedule(sheet, month_row: int, name: str, expected: list[str]):
    schedule = read_month_schedule(sheet, month_row)
    assert schedule[name][:3] == expected


# Тест определение статуса на день
@pytest.mark.parametrize("name, day, expected", [
    ("Береговой Е.О.", 1, "ONLINE"),
    ("Береговой Е.О.", 2, "OFFLINE"),
    ("Секачёв С.Ю.", 1, "OFFLINE"),
    ("Секачёв С.Ю.", 2, "ONLINE"),
    ("Секачёв С.Ю.", 3, "ONLINE"),
    ("Несуществующий И.И.", 1, None),
])
def test_status_for_day(schedule, name: str, day: int, expected: str | None):
    assert status_for_day(schedule, name, day) == expected

# Тест открытия валидного файла (бинарника)
def test_open_schedule_valid_file():
    workbook = openpyxl.Workbook()
    workbook.active.cell(row=1, column=NAME_COLUMN, value="ЯНВАРЬ")
    buff = io.BytesIO()
    workbook.save(buff)
    data = buff.getvalue()

    sheet = open_schedule(data, None)

    assert find_month_row(sheet, 1) == 1

# Тест некорректного файла
def test_open_schedule_invalid_file():
    with pytest.raises(ScheduleOpenError):
        open_schedule(b"wrong_way", None)

# Тест названий файла по году
@pytest.mark.parametrize("year,expected", [
    (2022, "График OEM 2022.xlsx"),
    (2027, "График OEM 2027.xlsx")])
def test_schedule_filename(year: int, expected: str):
    assert schedule_filename(year) == expected