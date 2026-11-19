from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Определяем корень проекта
basedir = Path(__file__).resolve().parent.parent
# Путь к папке с базами данных
databasedir = basedir / "databasedata"

# Пути к базе данных
usersdata = databasedir / "users.sqlite3"
productsdata = databasedir / "products.sqlite3"
# Создание движков для работы с базами
usersdatabaseengine = create_engine(f"sqlite:///{usersdata}",  connect_args={"check_same_thread": False})
productsdatabaseengine = create_engine(f"sqlite:///{productsdata}", connect_args={"check_same_thread": False})
#  Создание сессий под базы
UsersSession = sessionmaker(bind=usersdatabaseengine, autoflush=False, expire_on_commit=False)
ProductsSession = sessionmaker(bind=productsdatabaseengine, autoflush=False, expire_on_commit=False)

class UsersBase(DeclarativeBase):
    pass
class ProductsBase(DeclarativeBase):
    pass

def get_users_session():
    with UsersSession() as session:
        yield session
def get_products_session():
    with ProductsSession() as session:
        yield session