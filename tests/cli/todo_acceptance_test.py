import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

ROOT_DIR = Path(__file__).resolve().parents[2]
CLI_SRC_DIR = ROOT_DIR / "src" / "cli" / "src"
APP_SRC_DIR = ROOT_DIR / "src" / "app" / "src"

sys.path.insert(0, str(CLI_SRC_DIR))
sys.path.insert(0, str(APP_SRC_DIR))

sys.modules.pop("cli", None)
sys.modules.pop("app", None)

cli_main = importlib.import_module("cli.main")
app = cli_main.app
app_main = importlib.import_module("app.main")

runner = CliRunner()


class InProcessTodoApiClient:
    def __init__(self, client: TestClient) -> None:
        self.client = client

    def list_todos(self):
        response = self.client.get("/api/todos")
        response.raise_for_status()
        return [cli_main.Todo.model_validate(item) for item in response.json()]

    def create_todo(self, title: str, description: str | None = None):
        response = self.client.post("/api/todos", json={"title": title, "description": description})
        response.raise_for_status()
        return cli_main.Todo.model_validate(response.json())

    def update_todo(self, todo_id: int, title: str | None = None, description: str | None = None):
        response = self.client.put(f"/api/todos/{todo_id}", json={"title": title, "description": description})
        if response.status_code == 404:
            raise cli_main.TodoNotFoundError(response.json()["detail"])
        response.raise_for_status()
        return cli_main.Todo.model_validate(response.json())

    def delete_todo(self, todo_id: int) -> None:
        response = self.client.delete(f"/api/todos/{todo_id}")
        if response.status_code == 404:
            raise cli_main.TodoNotFoundError(response.json()["detail"])
        response.raise_for_status()

    def complete_todo(self, todo_id: int):
        response = self.client.post(f"/api/todos/{todo_id}/complete")
        if response.status_code == 404:
            raise cli_main.TodoNotFoundError(response.json()["detail"])
        response.raise_for_status()
        return cli_main.Todo.model_validate(response.json())

    def reopen_todo(self, todo_id: int):
        response = self.client.post(f"/api/todos/{todo_id}/reopen")
        if response.status_code == 404:
            raise cli_main.TodoNotFoundError(response.json()["detail"])
        response.raise_for_status()
        return cli_main.Todo.model_validate(response.json())


# Arrange for the test environment to be isolated and clean for each test case
@pytest.fixture(autouse=True)
def _prepare_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_DB_URL", f"sqlite+aiosqlite:///{tmp_path / 'todos.db'}")
    app_main.get_settings.cache_clear()

    with TestClient(app_main.app) as client:
        monkeypatch.setattr(cli_main, "get_api_client", lambda: InProcessTodoApiClient(client))
        yield

    app_main.get_settings.cache_clear()


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
