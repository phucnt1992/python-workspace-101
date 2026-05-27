from typing import NoReturn, Protocol

import typer
from domain.todo import Todo

from cli.todo.presentation.formatter import TodoFormatter


class TodoPresenter(Protocol):
    def show_empty_list(self) -> None: ...

    def show_todos(self, todos: list[Todo]) -> None: ...

    def show_todo(self, todo: Todo) -> None: ...

    def show_created(self, todo: Todo) -> None: ...

    def show_updated(self, todo: Todo) -> None: ...

    def show_deleted(self, todo_id: int) -> None: ...

    def exit_not_found(self, todo_id: int) -> NoReturn: ...


class TyperTodoPresenter:
    def __init__(self, formatter: TodoFormatter) -> None:
        self._formatter = formatter

    def show_empty_list(self) -> None:
        typer.echo("No todos found.")

    def show_todos(self, todos: list[Todo]) -> None:
        for todo in todos:
            self.show_todo(todo)

    def show_todo(self, todo: Todo) -> None:
        typer.echo(self._formatter.format(todo))

    def show_created(self, todo: Todo) -> None:
        typer.echo(f"Created todo: {self._formatter.format(todo)}")

    def show_updated(self, todo: Todo) -> None:
        typer.echo(f"Updated todo: {self._formatter.format(todo)}")

    def show_deleted(self, todo_id: int) -> None:
        typer.echo(f"Deleted todo with id={todo_id}.")

    def exit_not_found(self, todo_id: int) -> NoReturn:
        typer.echo(f"Todo with id={todo_id} was not found.")
        raise typer.Exit(code=1)
