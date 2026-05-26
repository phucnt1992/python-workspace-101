import asyncio

import typer
from domain.todo import Todo
from infra.db import get_session_context, init_db
from use_cases.todo import (
    create_todo,
    delete_todo,
    get_todo_list,
    set_todo_completed,
    update_todo,
)

from todocli.exp import app as exp_app

app = typer.Typer(help="Todo management CLI")
todo_app = typer.Typer(help="Create and manage todo items")


app.add_typer(todo_app, name="todo")
app.add_typer(exp_app, name="demo")


def _format_todo(todo: Todo) -> str:
    status = "x" if todo.completed else " "
    description = f" - {todo.description}" if todo.description else ""
    return f"{todo.id}. [{status}] {todo.title}{description}"


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
    description: str | None = typer.Option(None, "--description", "-d", help="Optional todo description"),
) -> None:
    async def _create() -> Todo:
        await init_db()
        async with get_session_context() as session:
            result = await create_todo(session, title=title, description=description)
            return result

    todo = asyncio.run(_create())
    typer.echo(f"Created todo:{_format_todo(todo=todo)}")


@todo_app.command("update")
def update(
    todo_id: int = typer.Argument(..., help="ID of the todo item to update"),
    title: str | None = typer.Option(None, "--title", "-t", help="New title"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
) -> None:
    async def _update() -> Todo | None:
        await init_db()
        async with get_session_context() as session:
            result = await update_todo(session, todo_id=todo_id, title=title, description=description)
            return result

    todo = asyncio.run(_update())
    if todo:
        typer.echo(f"Updated todo:{_format_todo(todo=todo)}")
    else:
        typer.echo(f"Todo with ID {todo_id} was not found")
        raise typer.Exit(code=1)


@todo_app.command("delete")
def delete(todo_id: int = typer.Argument(..., help="ID of the todo item to delete")) -> None:
    async def _delete(todo_id) -> bool:
        await init_db()
        async with get_session_context() as session:
            result = await delete_todo(session, todo_id=todo_id)
            return result

    result = asyncio.run(_delete(todo_id))
    if result:
        typer.echo(f"Deleted todo with id={str(todo_id)}.")


@todo_app.command("complete")
def complete(todo_id: int = typer.Argument(..., help="ID of the todo item to mark as completed")) -> None:
    async def _set_todo_completed(todo_id) -> Todo | None:
        await init_db()
        async with get_session_context() as session:
            result = await set_todo_completed(session, todo_id, True)
            return result

    result = asyncio.run(_set_todo_completed(todo_id))
    if result:
        typer.echo(_format_todo(result))


@todo_app.command("reopen")
def reopen(todo_id: int = typer.Argument(..., help="ID of the todo item to reopen")) -> None:
    async def _set_todo_not_completed(todo_id) -> Todo | None:
        await init_db()
        async with get_session_context() as session:
            result = await set_todo_completed(session, todo_id, False)
            return result

    result = asyncio.run(_set_todo_not_completed(todo_id))
    if result:
        typer.echo(_format_todo(result))


if __name__ == "__main__":
    app()
