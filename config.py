from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    GLADIA_API_KEY: str
    OPENROUTER_API_KEY: str
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


config = Config()  # type: ignore
