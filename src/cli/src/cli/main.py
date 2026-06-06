import asyncio
import sys
from pathlib import Path

# Add src/cli/src to sys.path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent / "src"))

import typer
from typing import Optional
from domain.todo import Todo
from infra.db import get_session_context, init_db
from use_cases.todo import (
    create_todo,
    delete_todo,
    get_todo_by_id,
    get_todo_list,
    set_todo_completed,
    update_todo,
)

# Import exp_app conditionally to support direct file loading in tests
try:
    from cli.exp import app as exp_app
except ModuleNotFoundError:
    exp_app = None

app = typer.Typer(help="Todo management CLI")
todo_app = typer.Typer(help="Create and manage todo items")


app.add_typer(todo_app, name="todo")
if exp_app is not None:
    app.add_typer(exp_app, name="demo")


def _format_todo(todo: Todo) -> str:
    status = "x" if todo.completed else " "
    description = f" - {todo.description}" if todo.description else ""
    return f"{todo.id}. [{status}] {todo.title}{description}"


def _logger_with_checking_todo_exist(
    result: Todo | bool | None,
    todo_id: str,
    success_message: Optional[str] = None,
) -> None:
    if result:
        if success_message:
            typer.echo(success_message)
        if isinstance(result, Todo):
            typer.echo(f"{_format_todo(result)}")
    else:
        typer.echo(f"Todo with id={todo_id} was not found.")
        sys.exit(1)


@todo_app.command("list")
def list_todos() -> None:
    async def _list() -> list[Todo]:
        await init_db()
        async with get_session_context() as session:
            result = await get_todo_list(session)
            return list(result)

    todos = asyncio.run(_list())
    if not todos:
        typer.echo("No todos found.")
        return

    for todo in todos:
        typer.echo(_format_todo(todo))


@todo_app.command("create")
def create(
    title: str = typer.Argument(..., help="Title of the todo item"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Optional todo description"
    ),
) -> None:
    async def _create() -> Todo:
        await init_db()
        async with get_session_context() as session:
            return await create_todo(session, title, description)

    todo = asyncio.run(_create())
    typer.echo(f"Created todo: {_format_todo(todo)}")


@todo_app.command("update")
def update(
    todo_id: int = typer.Argument(..., help="ID of the todo item to update"),
    title: str | None = typer.Option(None, "--title", "-t", help="New title"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="New description"
    ),
) -> None:
    async def _update() -> Todo:
        await init_db()
        async with get_session_context() as session:
            return await update_todo(session, todo_id, title, description)

    updated_todo = asyncio.run(_update())
    _logger_with_checking_todo_exist(updated_todo, todo_id, "Updated todo:")


@todo_app.command("delete")
def delete(
    todo_id: int = typer.Argument(..., help="ID of the todo item to delete")
) -> None:
    async def _delete() -> Todo:
        await init_db()
        async with get_session_context() as session:
            return await delete_todo(session, todo_id)

    deleted_todo = asyncio.run(_delete())
    _logger_with_checking_todo_exist(
        deleted_todo, todo_id, f"Deleted todo with id={todo_id}."
    )


@todo_app.command("complete")
def complete(
    todo_id: int = typer.Argument(..., help="ID of the todo item to mark as completed")
) -> None:
    async def _complete() -> Todo:
        await init_db()
        async with get_session_context() as session:
            return await set_todo_completed(session, todo_id, True)

    completed_todo = asyncio.run(_complete())
    _logger_with_checking_todo_exist(completed_todo, todo_id)


@todo_app.command("reopen")
def reopen(
    todo_id: int = typer.Argument(..., help="ID of the todo item to reopen")
) -> None:
    async def _reopen() -> Todo:
        await init_db()
        async with get_session_context() as session:
            return await set_todo_completed(session, todo_id, False)

    reopened_todo = asyncio.run(_reopen())
    _logger_with_checking_todo_exist(reopened_todo, todo_id)


if __name__ == "__main__":
    app()
