
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

# Ошибка работы с графиком
class ScheduleError(Exception):
    """Общая ошибка работы с графиком."""

# Ошибка в графике нет нужного блока месяца
class MonthNotFoundError(ScheduleError):
    """В графике нет блока нужного месяца."""

# Нормализация имени
def normalize_name(name: object) -> str:
    if not isinstance(name, str):
        return ""
    # Обработка букв ё на е и Ё на Е
    name = name.replace("ё", "е").replace("Ё", "Е")
    # Убираем пробелы
    name = " ".join(name.split())
    return name.upper()

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

