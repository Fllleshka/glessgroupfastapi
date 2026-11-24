from sqlalchemy.orm import Session
from sqlalchemy import select

from database.models import Users

# Функция поиска короткого номера в базе
def get_manager_by_shortnumber(session: Session, shortnumber: int) -> Users | None:
    return session.scalar(select(Users).where(Users.shortnumber == shortnumber))

# Функция выборки сотрудников для call-центра
def get_callcenter_managers(session: Session) -> list[Users]:
    query = select(Users).where(Users.callcenter.is_(True), Users.shortnumber.is_not(None)).order_by(Users.key)
    return list(session.scalars(query))