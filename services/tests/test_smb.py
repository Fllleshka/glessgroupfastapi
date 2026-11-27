"""Тесты чтения файла по SMB: read_smb_file.

Настоящий сетевой диск не используется: smbclient.open_file подменяется заглушкой,
которая возвращает байты или бросает ту ошибку, которую бросил бы smbprotocol.
time.sleep тоже подменяется, чтобы тесты не ждали паузы между попытками.
"""
import io
from types import SimpleNamespace

import pytest
from pydantic import SecretStr
from smbprotocol.exceptions import SMBOSError
from smbprotocol.header import NtStatus

from services import smb

PATH = r"\\server\share\file.xlsx"


# Тестовые настройки вместо .env
@pytest.fixture(autouse=True)
def fake_settings(monkeypatch):
    settings = SimpleNamespace(smb_user="DOMAIN\\user", smb_password=SecretStr("secret"))
    monkeypatch.setattr(smb, "get_settings", lambda: settings)


# Паузы между попытками не ждём, а только считаем
@pytest.fixture
def sleeps(monkeypatch):
    calls = []
    monkeypatch.setattr(smb.time, "sleep", lambda seconds: calls.append(seconds))
    return calls


# Заглушка open_file: по очереди отдаёт заготовленные результаты.
# Результат-исключение бросается, результат-байты возвращается как содержимое файла.
@pytest.fixture
def fake_open(monkeypatch):
    state = SimpleNamespace(results=[], calls=[])

    def open_file(path, **kwargs):
        state.calls.append((path, kwargs))
        result = state.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return io.BytesIO(result)

    monkeypatch.setattr(smb.smbclient, "open_file", open_file)
    return state


# Файл прочитан с первой попытки; проверяем, с какими параметрами открывали
def test_read_success(fake_open, sleeps):
    fake_open.results = [b"file content"]

    assert smb.read_smb_file(PATH) == b"file content"

    path, kwargs = fake_open.calls[0]
    assert path == PATH
    assert kwargs["mode"] == "rb"
    assert kwargs["username"] == "DOMAIN\\user"
    assert kwargs["password"] == "secret"
    assert kwargs["share_access"] == "rw"
    assert kwargs["connection_timeout"] == smb.SMB_TIMEOUT
    assert sleeps == []


# Файла нет: сразу SmbFileNotFoundError, без повторов
def test_file_not_found(fake_open, sleeps):
    fake_open.results = [SMBOSError(NtStatus.STATUS_OBJECT_NAME_NOT_FOUND, PATH)]

    with pytest.raises(smb.SmbFileNotFoundError):
        smb.read_smb_file(PATH)

    assert len(fake_open.calls) == 1
    assert sleeps == []


# Неверный логин или пароль: сразу SmbUnavailableError, без повторов
# (повторы с неверным паролем могут заблокировать учётную запись в домене)
def test_logon_failure(fake_open, sleeps):
    fake_open.results = [SMBOSError(NtStatus.STATUS_LOGON_FAILURE, PATH)]

    with pytest.raises(smb.SmbUnavailableError):
        smb.read_smb_file(PATH)

    assert len(fake_open.calls) == 1


# Сервер недоступен каждый раз: все попытки, паузы между ними, затем SmbUnavailableError
def test_server_unavailable(fake_open, sleeps):
    fake_open.results = [ValueError("Failed to connect")] * smb.READ_ATTEMPTS

    with pytest.raises(smb.SmbUnavailableError):
        smb.read_smb_file(PATH)

    assert len(fake_open.calls) == smb.READ_ATTEMPTS
    assert sleeps == [smb.READ_DELAY] * (smb.READ_ATTEMPTS - 1)


# Первая попытка не удалась, вторая прошла: файл прочитан
def test_retry_then_success(fake_open, sleeps):
    fake_open.results = [ValueError("Failed to connect"), b"file content"]

    assert smb.read_smb_file(PATH) == b"file content"
    assert len(fake_open.calls) == 2
    assert sleeps == [smb.READ_DELAY]