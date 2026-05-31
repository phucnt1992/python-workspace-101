import asyncio
import os
from collections.abc import Generator

import pytest
from api.main import app  # type: ignore
from docker.errors import DockerException
from fastapi.testclient import TestClient
from infra.db import reset_engine
from infra.settings import get_settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from testcontainers.postgres import PostgresContainer


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _force_ipv4_localhost(url: str) -> str:
    return url.replace("localhost", "127.0.0.1")


async def _reset_database(db_url: str) -> None:
    engine = create_async_engine(db_url)
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        await connection.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()


def _local_postgres_url() -> str:
    return _force_ipv4_localhost(
        _to_asyncpg_url(
            os.environ.get(
                "APP_DB_URL",
                "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/todos",
            )
        )
    )


@pytest.fixture
def postgres_env() -> Generator[str, None, None]:
    local_db_url = _local_postgres_url()
    old_db_url = os.environ.get("APP_DB_URL")

    try:
        with PostgresContainer("postgres:18-alpine") as postgres:
            db_url = _to_asyncpg_url(postgres.get_connection_url())
            os.environ["APP_DB_URL"] = db_url
            get_settings.cache_clear()
            reset_engine()
            yield db_url
    except DockerException:
        try:
            os.environ["APP_DB_URL"] = local_db_url
            get_settings.cache_clear()
            reset_engine()
            asyncio.run(_reset_database(local_db_url))
            yield local_db_url
        except Exception:
            sqlite_db_url = "sqlite+aiosqlite:///./test_todos.db"
            os.environ["APP_DB_URL"] = sqlite_db_url
            get_settings.cache_clear()
            reset_engine()
            asyncio.run(_reset_database(sqlite_db_url))
            yield sqlite_db_url
    finally:
        if old_db_url is None:
            os.environ.pop("APP_DB_URL", None)
        else:
            os.environ["APP_DB_URL"] = old_db_url
        get_settings.cache_clear()
        reset_engine()


@pytest.fixture
def client(postgres_env: str) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
