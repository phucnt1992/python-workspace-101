import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from api.main import app
from infra.db import reset_engine
from infra.settings import get_settings
from testcontainers.postgres import PostgresContainer


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


@pytest.fixture
def postgres_env() -> Generator[str, None, None]:
    with PostgresContainer("postgres:16-alpine") as postgres:
        db_url = _to_asyncpg_url(postgres.get_connection_url())
        old_db_url = os.environ.get("APP_DB_URL")
        os.environ["APP_DB_URL"] = db_url
        get_settings.cache_clear()
        reset_engine()
        yield db_url
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
