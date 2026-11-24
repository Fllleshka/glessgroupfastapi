import logging
from typing import Literal
# Библиотека для работы с HTTP запросами
import requests
# Работа с секретами
from config import get_settings
# Логгер для модуля
logger = logging.getLogger(__name__)

def set_agent_status(shortnumber: int, status: Literal["ONLINE", "OFFLINE"]) -> str:
    # Подгружаем настройки
    settings = get_settings()
    # Формируем параметры для работы
    url = f"{settings.beeline_api_url}{shortnumber}/agent"
    headers = {settings.beeline_header_name: settings.beeline_token.get_secret_value()}
    params = {'status': status}
    # Выполняем запрос
    response = requests.put(url,
                 params = params,
                 headers = headers,
                 timeout = 10)
    response.raise_for_status()
    # Получаем актуальный статус менеджера
    statusget = requests.get(url,
                             headers=headers,
                             timeout = 10)
    statusget.raise_for_status()
    agent_status = statusget.json()
    logger.info(f"Выполнена настройка менеджера: {shortnumber}. Теперь статус: {agent_status}")
    # Возвращаем статус
    return agent_status