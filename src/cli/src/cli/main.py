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
    todo_id: int,
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


async def _call_function_by_name(function_name: str, **kwargs):
    if function_name in globals() and callable(globals()[function_name]):
        await init_db()
        async with get_session_context() as session:
            result = await globals()[function_name](session, **kwargs)
            return result
    else:
        typer.echo(f"Function {function_name} does not exist!")
        sys.exit(1)


@todo_app.command("list")
def list_todos() -> None:
    todos = asyncio.run(_call_function_by_name("get_todo_list"))
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
    kwargs = {"title": title, "description": description}
    todo = asyncio.run(_call_function_by_name("create_todo", **kwargs))
    typer.echo(f"Created todo: {_format_todo(todo)}")


@todo_app.command("update")
def update(
    todo_id: int = typer.Argument(..., help="ID of the todo item to update"),
    title: str | None = typer.Option(None, "--title", "-t", help="New title"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="New description"
    ),
) -> None:
    kwargs = {"todo_id": todo_id, "title": title, "description": description}
    updated_todo = asyncio.run(_call_function_by_name("update_todo", **kwargs))
    _logger_with_checking_todo_exist(updated_todo, todo_id, "Updated todo:")


@todo_app.command("delete")
def delete(
    todo_id: int = typer.Argument(..., help="ID of the todo item to delete")
) -> None:
    kwargs = {
        "todo_id": todo_id,
    }
    deleted_todo = asyncio.run(_call_function_by_name("delete_todo", **kwargs))

    _logger_with_checking_todo_exist(
        deleted_todo, todo_id, f"Deleted todo with id={todo_id}."
    )


@todo_app.command("complete")
def complete(
    todo_id: int = typer.Argument(..., help="ID of the todo item to mark as completed")
) -> None:
    kwargs = {"todo_id": todo_id, "completed": True}
    completed_todo = asyncio.run(_call_function_by_name("set_todo_completed", **kwargs))
    _logger_with_checking_todo_exist(completed_todo, todo_id)


@todo_app.command("reopen")
def reopen(
    todo_id: int = typer.Argument(..., help="ID of the todo item to reopen")
) -> None:
    kwargs = {"todo_id": todo_id, "completed": False}
    reopened_todo = asyncio.run(_call_function_by_name("set_todo_completed", **kwargs))
    _logger_with_checking_todo_exist(reopened_todo, todo_id)


if __name__ == "__main__":
    app()
