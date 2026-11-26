from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

basedir = Path(__file__).resolve().parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=basedir / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Билайн
    beeline_api_url: str = Field(validation_alias="BEELINEAPIURL")
    beeline_header_name: str = Field(validation_alias="BEELINEAPIHEADERMETOD")
    beeline_token: SecretStr = Field(validation_alias="BEELINEAPIHEADERTOKEN")

    # Уведомления
    telegram_bot_key: SecretStr = Field(validation_alias="TELEGRAMBOTKEY")
    admin_telegram_id: int = Field(validation_alias="ADMINTELEGRAMID")

    # Google Sheets
    unknown_sheet_cell: str = Field(validation_alias="UNKNOWNSHEETCELL")

    # График
    smb_user: str = Field(validation_alias="FASTAPISMBUSER")
    smb_password: SecretStr = Field(validation_alias="FASTAPISMBPASSWORD")
    schedule_folder: str = Field(validation_alias="SCHEDULEFOLDER")
    schedule_password: SecretStr = Field(validation_alias="EXCELPASSWORDMAINFILE")

@lru_cache
def get_settings() -> Settings:
    return Settings()