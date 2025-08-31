from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


config = Config()  # type: ignore
