import database.models

from database.engine import usersdatabaseengine
from database.engine import productsdatabaseengine
from database.engine import UsersBase
from database.engine import ProductsBase

# Инициализация таблиц и баз данных
def init_database() -> None:
    UsersBase.metadata.create_all(usersdatabaseengine)
    ProductsBase.metadata.create_all(productsdatabaseengine)

# Закрытия соединения при остановке приложения
def close_database() -> None:
    usersdatabaseengine.dispose()
    productsdatabaseengine.dispose()