import os
from collections.abc import Generator
from pathlib import Path

import pytest
from api.main import app  # type: ignore
from fastapi.testclient import TestClient
from infra.db import reset_engine
from infra.settings import get_settings


@pytest.fixture
def db_env(tmp_path: Path) -> Generator[str, None, None]:
    db_file = tmp_path / "todos.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
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
def client(db_env: str) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
