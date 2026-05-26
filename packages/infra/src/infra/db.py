from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, AsyncIterator

from fastapi import Depends
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import get_settings

_engine: AsyncEngine | None = None
_db_instrumented = False


def get_engine() -> AsyncEngine:
    global _engine, _db_instrumented
    if _engine is None:
        _engine = create_async_engine(get_settings().db_url)
    if not _db_instrumented:
        SQLAlchemyInstrumentor().instrument(engine=_engine.sync_engine)
        _db_instrumented = True
    return _engine


def reset_engine() -> None:
    global _engine, _db_instrumented
    _engine = None
    _db_instrumented = False


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def dispose_engine() -> None:
    global _engine, _db_instrumented
    if _engine is not None:
        SQLAlchemyInstrumentor().uninstrument()
        await _engine.dispose()
        _engine = None
        _db_instrumented = False


@asynccontextmanager
async def get_session_context() -> AsyncIterator[AsyncSession]:
    engine = get_engine()
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()


# Dependency to get an async database session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_context() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
