from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Super Simple App"
    debug: bool = False
    db_url: str = "sqlite+aiosqlite:///./todos.db"
    model_config = SettingsConfigDict(env_prefix="APP_")


# Singleton pattern for settings
@lru_cache
def get_settings() -> Settings:
    return Settings()
