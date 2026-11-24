import os
import logging
from dotenv import load_dotenv

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic import field_validator, computed_field, model_validator
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.engine import basedir, UsersSession
from database.models import Users

# Логгер для модуля
logger = logging.getLogger(__name__)
# Префикс всех сотрудников в .env
envprefix = "USER_"
# Модель о данных о сотруднике
envfields = {
    "FIRSTNAME": "secondname",
    "SECONDNAME": "firstname",
    "PATRONYMIC": "patronymic",
    "SHORTNUMBER": "shortnumber",
    "SID": "sid",
    "DATEFORSHEETS": "dateforsheets",
    "TELEGRAMID": "telegramid",
    "CALLCENTER": "callcenter"
}

# Функция импорта данных о сотрудниках из env
def readusersfromenv(environ: Mapping[str, str] = os.environ) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, str]] = defaultdict(dict)

    for name, value in environ.items():
        if not name.startswith(envprefix):
            continue
        rest = name.removeprefix(envprefix)
        key, sep, field = rest.rpartition("_")

        if not sep or not key or field not in envfields:
            continue

        grouped[key][envfields[field]] = value

    return [{"key": key, **fields} for key, fields in sorted(grouped.items())]

# Создаем класс для верификации данных
class UserSeed(BaseModel):
    #  Общие правила для всей модели
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    # Ключ
    key: str = Field(max_length=50)
    # Имя
    firstname: str = Field(min_length=1, max_length=100)
    # Фамилия
    secondname: str = Field(min_length=1, max_length=100)
    # Отчество
    patronymic: str = Field(min_length=1, max_length=100)
    # Коротки номер Beeline
    shortnumber: int | None = None
    # SID в системе
    sid: str | None = Field(default=None, max_length=200)
    # Массив ячеек для заполнения в googlesheets
    dateforsheets: str | None = Field(default=None, max_length=20)
    # ID в телеграмме
    telegramid: int | None = None
    # Флаг отношения к call центру
    callcenter: bool = False

    # Проверка полей до приведения типов
    @field_validator("shortnumber", "sid", "dateforsheets", "telegramid", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    # Проверка поля call центр, для выборки
    @field_validator('callcenter', mode="before")
    @classmethod
    def empty_callcenter_to_false(cls, value):
        if isinstance(value, str) and not value.strip():
            return False
        return value


    # Вычисляем короткое ФИО
    @computed_field
    @property
    def shortname(self) -> str:
        initials = "".join(f"{part[0]}." for part in (self.firstname, self.patronymic) if part)
        return f"{self.secondname} {initials}"

    # Вычисляем полное ФИО
    @computed_field
    @property
    def fullname(self) -> str:
        result = f"{self.secondname} {self.firstname} {self.patronymic}"
        return result

    # Проверка всей модели после вычислений
    @model_validator(mode="after")
    def check_computed_lengths(self):
        if len(self.fullname) > 150:
            raise ValueError(
                f"fullname длиннее 150 символов: {len(self.fullname)}")
        if len(self.shortname) > 100:
            raise ValueError(
                f"shortname длиннее 100 символов: {len(self.shortname)}")
        return self

    #

# Итог синхронизации: сколько записей добавлено, обновлено и осталось без изменений
@dataclass(frozen=True)
class SyncResult:
    created: int = 0
    updated: int = 0
    unchanged: int = 0


# Записывает сотрудников в базу: новых добавляет, у существующих обновляет изменившиеся поля
def syncusers(session: Session, seeds: list[UserSeed]) -> SyncResult:
    # Все, кто уже есть в базе, одним запросом: {key: Users}
    keys = [seed.key for seed in seeds]
    existing = {user.key: user for user in session.scalars(select(Users).where(Users.key.in_(keys)))}

    created = updated = unchanged = 0
    for seed in seeds:
        values = seed.model_dump()
        user = existing.get(seed.key)

        # Новый сотрудник
        if user is None:
            session.add(Users(**values))
            created += 1
            continue

        # Существующий: меняем только то, что отличается
        changes = {column: value for column, value in values.items() if getattr(user, column) != value}
        if changes:
            for column, value in changes.items():
                setattr(user, column, value)
            updated += 1
        else:
            unchanged += 1

    # Одна транзакция на всё: либо записалось всё, либо ничего
    session.commit()
    return SyncResult(created=created, updated=updated, unchanged=unchanged)

# Загружает сотрудников из .env в базу. Вызывается при старте приложения
def initusers() -> SyncResult | None:
    load_dotenv(basedir / ".env")

    # Проверяем каждого сотрудника; с ошибкой — пропускаем, остальных загружаем
    seeds: list[UserSeed] = []
    for data in readusersfromenv():
        try:
            seeds.append(UserSeed(**data))
        except ValidationError as e:
            logger.error(f"Сотрудник {data.get('key')} пропущен, ошибка в .env: {e}")

    if not seeds:
        logger.warning("В .env нет сотрудников (USER_<КЛЮЧ>_<ПОЛЕ>), таблица users не изменена")
        return None

    with UsersSession() as session:
        result = syncusers(session, seeds)

    logger.info(f"Таблица users: добавлено {result.created}, обновлено {result.updated}, "
                f"без изменений {result.unchanged}")
    return result