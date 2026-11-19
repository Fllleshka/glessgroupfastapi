from sqlalchemy import String, Integer, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import UsersBase, ProductsBase

class Users(UsersBase):
    __tablename__ = "users"
    # id
    id: Mapped[int] = mapped_column(primary_key = True)
    # Имя
    firstname: Mapped[str] = mapped_column(String(100))
    # Фамилия
    lastname: Mapped[str] = mapped_column(String(100))
    # Отчество
    patronymic: Mapped[str] = mapped_column(String(100))
    # Короткое ФИО
    shortname: Mapped[str] = mapped_column(String(100))
    # Полное имя
    fullname: Mapped[str] = mapped_column(String(150))
    # Коротки номер Beeline
    shortnumber: Mapped[int] = mapped_column(Integer, default = None)
    # SID в системе (идентификатор win32, дается при установке windows)
    idinwindows: Mapped[str] = mapped_column(String(200), default = None)
    # Массив ячеек для заполнения в googlesheets
    dateforsheets: Mapped[str] = mapped_column(String(20), default = None)
    # ID в телеграмме
    idintelegram: Mapped[str] = mapped_column(BigInteger, default = None)

class Products(ProductsBase):
    __tablename__ = "products"
    # id
    id: Mapped[int] = mapped_column(primary_key = True)
    # id в 1С
    id_in_1c: Mapped[int] = mapped_column(Integer, index = True, unique = True)
    # Название детали
    name: Mapped[str] = mapped_column(String(200))
    # Вкладка в каталоге
    tab: Mapped[int] = mapped_column(Integer)
    # Производитель
    brand: Mapped[str] = mapped_column(String(100))
    # Модели машин
    model: Mapped[str] = mapped_column(String(200))
    # Кузов
    body: Mapped[str] = mapped_column(String(100))
    # Года производства
    years: Mapped[str] = mapped_column(String(200))
    # Двигатель
    engine: Mapped[str] = mapped_column(String(200))
    # Состояние (новый или б/у)
    state: Mapped[str] = mapped_column(String(50))
    # Производитель
    producer: Mapped[str] = mapped_column(String(100))
    # Каталожный номер детали
    number: Mapped[str] = mapped_column(String(50))
    # Сторона (правая или левая)
    side: Mapped[str] = mapped_column(String(20))
    # Часть машины (передняя или задняя)
    front_back: Mapped[str] = mapped_column(String(20))
    # Количество
    amount: Mapped[int] = mapped_column(Integer)
    # Цена
    price: Mapped[int] = mapped_column(Integer)
    # Наличие
    availability: Mapped[str] = mapped_column(String(50))
    # Описание
    direction: Mapped[str] = mapped_column(Text)
    # Новинка
    new: Mapped[str] = mapped_column(String(100))
    # Название в интернете
    name_internet: Mapped[str] = mapped_column(String(200))
    # Положение (верх или низ)
    up_down: Mapped[str] = mapped_column(String(20))
    # Коробка передач (автомат, механика и др.)
    transmission: Mapped[str] = mapped_column(String(50))
    # Привод
    drive: Mapped[str] = mapped_column(String(50))
    # Тип кузова
    type_body: Mapped[str] = mapped_column(String(50))
    # Синонимы
    synonym: Mapped[str] = mapped_column(String(200))