import logging
import errno
import time
# Библиотека для получения файла по smb
import smbclient

from smbprotocol.exceptions import SMBOSError
from config import get_settings

SMB_TIMEOUT = 10
READ_ATTEMPTS = 3
READ_DELAY = 3


# Объявление логгера
logger = logging.getLogger(__name__)

class SmbError(Exception):
    """Ошибка чтения файла по SMB"""

class SmbFileNotFoundError(SmbError):
    """Файла по указанному пути нет"""

class SmbUnavailableError(SmbError):
    """Сетевой диск недоступен или не удалось войти"""

# Чтение файла
def read_smb_file(path: str) -> bytes:
    # Импорт настроек
    settings = get_settings()
    # Читаем данные
    for attempt in range(1, READ_ATTEMPTS + 1):
        try:
            with smbclient.open_file(path,
                                mode = "rb",
                                username = settings.smb_user,
                                password = settings.smb_password.get_secret_value(),
                                share_access = "rw",
                                connection_timeout = SMB_TIMEOUT) as file:
                return file.read()
        except SMBOSError as e:
            if e.errno == errno.ENOENT:
                raise SmbFileNotFoundError(f"Файл {path} не найден.") from e
            raise SmbUnavailableError("Сетевой диск недоступен или неверные логин и пароль") from e
        except ValueError as e:
            logger.warning(f"Предупреждение открытия файла {path} попытка {attempt} не удалась")
            if attempt != READ_ATTEMPTS:
                time.sleep(READ_DELAY)
            last_error = e
    raise SmbUnavailableError(f"Файл недоступен, попыток: {READ_ATTEMPTS}") from last_error

