import typer
from domain.todo import Todo

from cli.api_client import TodoApiError, TodoNotFoundError, get_api_client
from cli.exp import app as exp_app

app = typer.Typer(help="Todo management CLI")
todo_app = typer.Typer(help="Create and manage todo items")


app.add_typer(todo_app, name="todo")
app.add_typer(exp_app, name="demo")


def _format_todo(todo: Todo) -> str:
    status = "x" if todo.completed else " "
    description = f" - {todo.description}" if todo.description else ""
    return f"{todo.id}. [{status}] {todo.title}{description}"


def _fail(message: str) -> None:
    typer.echo(message)
    raise typer.Exit(code=1)


@todo_app.command("list")
def list_todos() -> None:
    try:
        todos = get_api_client().list_todos()
    except TodoApiError as exc:
        _fail(str(exc))

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
    try:
        todo = get_api_client().create_todo(title=title, description=description)
    except TodoApiError as exc:
        _fail(str(exc))

    typer.echo(f"Created todo: {_format_todo(todo)}")


@todo_app.command("update")
def update(
    todo_id: int = typer.Argument(..., help="ID of the todo item to update"),
    title: str | None = typer.Option(None, "--title", "-t", help="New title"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
) -> None:
    try:
        todo = get_api_client().update_todo(todo_id=todo_id, title=title, description=description)
    except TodoNotFoundError:
        _fail(f"Todo with id={todo_id} was not found.")
    except TodoApiError as exc:
        _fail(str(exc))

    typer.echo(f"Updated todo: {_format_todo(todo)}")


@todo_app.command("delete")
def delete(todo_id: int = typer.Argument(..., help="ID of the todo item to delete")) -> None:
    try:
        get_api_client().delete_todo(todo_id=todo_id)
    except TodoNotFoundError:
        _fail(f"Todo with id={todo_id} was not found.")
    except TodoApiError as exc:
        _fail(str(exc))

    typer.echo(f"Deleted todo with id={todo_id}.")


@todo_app.command("complete")
def complete(todo_id: int = typer.Argument(..., help="ID of the todo item to mark as completed")) -> None:
    try:
        todo = get_api_client().complete_todo(todo_id=todo_id)
    except TodoNotFoundError:
        _fail(f"Todo with id={todo_id} was not found.")
    except TodoApiError as exc:
        _fail(str(exc))

    typer.echo(_format_todo(todo))


@todo_app.command("reopen")
def reopen(todo_id: int = typer.Argument(..., help="ID of the todo item to reopen")) -> None:
    try:
        todo = get_api_client().reopen_todo(todo_id=todo_id)
    except TodoNotFoundError:
        _fail(f"Todo with id={todo_id} was not found.")
    except TodoApiError as exc:
        _fail(str(exc))

    typer.echo(_format_todo(todo))


if __name__ == "__main__":
    app()
