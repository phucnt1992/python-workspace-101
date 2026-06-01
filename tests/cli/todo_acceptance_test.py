from pathlib import Path

import pytest
from cli.main import app
from infra.db import reset_engine
from infra.settings import get_settings
from typer.testing import CliRunner

runner = CliRunner()


# Arrange for the test environment to be isolated and clean for each test case
@pytest.fixture(autouse=True)
def _prepare_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    db_file = tmp_path / "todos.db"
    monkeypatch.setenv("APP_DB_URL", f"sqlite+aiosqlite:///{db_file}")
    get_settings.cache_clear()
    reset_engine()
    yield
    get_settings.cache_clear()
    reset_engine()


def test_create_then_list_todos() -> None:
    create_result = runner.invoke(app, ["todo", "create", "Buy milk", "--description", "2 bottles"])

    assert create_result.exit_code == 0
    assert "Created todo:" in create_result.stdout

    list_result = runner.invoke(app, ["todo", "list"])

    assert list_result.exit_code == 0
    assert "[ ] Buy milk - 2 bottles" in list_result.stdout


def test_update_existing_todo() -> None:
    runner.invoke(app, ["todo", "create", "Old title"])

    update_result = runner.invoke(
        app,
        ["todo", "update", "1", "--title", "New title", "--description", "Updated description"],
    )

    assert update_result.exit_code == 0
    assert "Updated todo:" in update_result.stdout
    assert "New title - Updated description" in update_result.stdout

    list_result = runner.invoke(app, ["todo", "list"])
    assert "New title - Updated description" in list_result.stdout


def test_delete_existing_todo() -> None:
    runner.invoke(app, ["todo", "create", "Disposable task"])

    delete_result = runner.invoke(app, ["todo", "delete", "1"])

    assert delete_result.exit_code == 0
    assert "Deleted todo with id=1." in delete_result.stdout

    list_result = runner.invoke(app, ["todo", "list"])
    assert "No todos found." in list_result.stdout


def test_non_existent_todo_returns_error() -> None:

    update_result = runner.invoke(app, ["todo", "update", "999", "--title", "Does not matter"])

    assert update_result.exit_code == 1
    assert "was not found" in update_result.stdout


def test_complete_and_reopen_todo() -> None:
    runner.invoke(app, ["todo", "create", "Finish report"])

    complete_result = runner.invoke(app, ["todo", "complete", "1"])
    assert complete_result.exit_code == 0
    assert "[x] Finish report" in complete_result.stdout

    reopen_result = runner.invoke(app, ["todo", "reopen", "1"])
    assert reopen_result.exit_code == 0
    assert "[ ] Finish report" in reopen_result.stdout
