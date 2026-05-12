from functools import lru_cache
from typing import AsyncGenerator, Optional, Union

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sqlmodel.ext.asyncio.session import AsyncSession


class Settings(BaseSettings):
    app_name: str = "Super Simple App"
    debug: bool = False
    db_url: Optional[Union[str, URL]]

    model_config = SettingsConfigDict(env_prefix="APP_")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Singleton pattern for settings
@lru_cache
def get_settings() -> Settings:
    return Settings()


#  Create DB Setting
DATABASE_URL = get_settings().db_url

assert DATABASE_URL, "DATABASE_URL is empty, it must be configured."

engine = create_async_engine(DATABASE_URL)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()


# Implement in /app/services/health_check_service.py
class HealthCheckStatus(BaseModel):
    status: str


class HealthCheckService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_database_connected(self) -> bool:
        try:
            result = await self.db.exec(text("SELECT 1;"))  # type: ignore
            return result.first() == (1,)
        except Exception:
            return False


def get_health_check_service(
    db: AsyncSession = Depends(get_db_session),
) -> HealthCheckService:
    return HealthCheckService(db)


app = FastAPI()


@app.get("/api/_healthz/liveness", tags=["healthz"], response_model=HealthCheckStatus)
def get_liveness_status():
    if not get_settings().db_url:
        raise HTTPException(status_code=503, detail={"status": "error"})

    return {"status": "ok"}


@app.get("/api/_healthz/readiness", tags=["healthz"], response_model=HealthCheckStatus)
async def get_readiness_status(
    service: HealthCheckService = Depends(get_health_check_service),
):
    result = await service.is_database_connected()

    if result.first() == (1,):
        return {"status": "ok"}

    raise HTTPException(status_code=503, detail={"status": "error"})
