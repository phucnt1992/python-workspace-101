from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Super Simple App"
    debug: bool = False
    db_url: str = "sqlite+aiosqlite:///./todos.db"
    otel_service_name: str = "todo-api"
    model_config = SettingsConfigDict(env_prefix="APP_")

    @model_validator(mode="after")
    def normalize_db_url(self) -> "Settings":
        # Aspire injects PostgreSQL connection strings as postgresql:// or postgres://.
        # SQLAlchemy asyncpg driver requires the postgresql+asyncpg:// scheme.
        for plain in ("postgresql://", "postgres://"):
            if self.db_url.startswith(plain):
                self.db_url = "postgresql+asyncpg://" + self.db_url[len(plain) :]
                break
        return self


# Singleton pattern for settings
@lru_cache
def get_settings() -> Settings:
    return Settings()
