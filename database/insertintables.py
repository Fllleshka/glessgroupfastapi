import os
from collections import defaultdict
from collections.abc import Mapping

# Префикс всех сотрудников в .env
envprefix = "USER_"
# Модель о данных о сотруднике
envfields = {
    "FIRSTNAME": "firstname",
    "SECONDNAME": "secondname",
    "PATRONYMIC": "patronymic",
    "SHORTNUMBER": "shortnumber",
    "SID": "sid",
    "DATEFORSHEETS": "dateforsheets",
    "TELEGRAMID": "telegramid"
}

# Функция импорта данных о сотрудниках из env
def readusersfromenv(environ: Mapping[str, str] = os.environ) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, str]] = defaultdict(dict)

    for name, value in environ.items():
        if not name.startswith(envprefix):
            continue

        # USER_IVANOV_PETR_FIRSTNAME → "IVANOV_PETR_FIRSTNAME" → ("IVANOV_PETR", "FIRSTNAME")
        rest = name.removeprefix(envprefix)
        key, sep, field = rest.rpartition("_")

        if not sep or not key or field not in envfields:
            continue

        grouped[key][envfields[field]] = value

    return [{"key": key, **fields} for key, fields in sorted(grouped.items())]