from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql import text
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from domain.todo import Todo
from use_cases.todo import (
    create_todo as create_todo_use_case,
    delete_todo as delete_todo_use_case,
    get_todo_list as get_todo_list_use_case,
    set_todo_completed as set_todo_completed_use_case,
    update_todo as update_todo_use_case,
)


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


# Engine is initialized during application startup
_engine: Optional[AsyncEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _engine
    db_url = get_settings().db_url
    if not db_url:
        raise ValueError("APP_DB_URL environment variable is required but not configured.")
    _engine = create_async_engine(db_url)
    async with _engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    yield
    if _engine:
        await _engine.dispose()
        _engine = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if _engine is None:
        raise RuntimeError(
            "Database engine is not initialized. "
            "This should not happen during normal request handling. "
            "Please check application startup logs."
        )
    async with AsyncSession(_engine) as session:
        try:
            yield session
        finally:
            await session.close()


# Implement in /app/services/health_check_service.py
class HealthCheckStatus(BaseModel):
    status: str


class CreateTodoRequest(BaseModel):
    title: str
    description: str | None = None


class UpdateTodoRequest(BaseModel):
    title: str | None = None
    description: str | None = None


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


app = FastAPI(lifespan=lifespan)


@app.get("/api/_healthz/liveness", tags=["healthz"], response_model=HealthCheckStatus)
def get_liveness_status():
    if not get_settings().db_url:
        raise HTTPException(status_code=503, detail={"status": "error"})

    return {"status": "ok"}


@app.get("/api/_healthz/readiness", tags=["healthz"], response_model=HealthCheckStatus)
async def get_readiness_status(
    service: HealthCheckService = Depends(get_health_check_service),
):
    is_connected = await service.is_database_connected()

    if is_connected:
        return {"status": "ok"}

    raise HTTPException(status_code=503, detail={"status": "error"})


@app.get("/api/todos", tags=["todos"], response_model=list[Todo])
async def list_todos(db: AsyncSession = Depends(get_db_session)) -> list[Todo]:
    todos = await get_todo_list_use_case(db)
    return list(todos)


@app.post("/api/todos", tags=["todos"], response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(request: CreateTodoRequest, db: AsyncSession = Depends(get_db_session)) -> Todo:
    return await create_todo_use_case(db, title=request.title, description=request.description)


@app.put("/api/todos/{todo_id}", tags=["todos"], response_model=Todo)
async def update_todo(todo_id: int, request: UpdateTodoRequest, db: AsyncSession = Depends(get_db_session)) -> Todo:
    todo = await update_todo_use_case(db, todo_id=todo_id, title=request.title, description=request.description)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} was not found.")
    return todo


@app.delete("/api/todos/{todo_id}", tags=["todos"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db_session)) -> Response:
    deleted = await delete_todo_use_case(db, todo_id=todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} was not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/api/todos/{todo_id}/complete", tags=["todos"], response_model=Todo)
async def complete_todo(todo_id: int, db: AsyncSession = Depends(get_db_session)) -> Todo:
    todo = await set_todo_completed_use_case(db, todo_id=todo_id, completed=True)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} was not found.")
    return todo


@app.post("/api/todos/{todo_id}/reopen", tags=["todos"], response_model=Todo)
async def reopen_todo(todo_id: int, db: AsyncSession = Depends(get_db_session)) -> Todo:
    todo = await set_todo_completed_use_case(db, todo_id=todo_id, completed=False)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} was not found.")
    return todo
