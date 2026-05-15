from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import get_settings


def get_engine():
    return create_async_engine(get_settings().db_url)


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()


@asynccontextmanager
async def get_session_context() -> AsyncIterator[AsyncSession]:
    engine = get_engine()
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()
            await engine.dispose()


# Dependency to get an async database session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_context() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
