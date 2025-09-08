from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevels(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Config(BaseSettings):
    GLADIA_API_KEY: str
    OPENROUTER_API_KEY: str

    DB_URL: str

    ALGORITHM: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    EMAIL_SENDER: str
    EMAIL_SENDER_PASS: str

    HOST: str

    LOG_LEVEL: LogLevels

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


config = Config()  # type: ignore
