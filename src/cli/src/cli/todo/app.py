import typer

from cli.todo.application import TodoCommands
from cli.todo.shell import TodoShell


class ToDoApp:
    def __init__(self, commands: TodoCommands) -> None:
        self._commands = commands
        self.typer = typer.Typer(help="Create and manage todo items", name="todo")
        self._register_commands()

    def _register_commands(self) -> None:
        commands = self._commands

        @self.typer.command("list")
        def list_todos() -> None:
            """List all todo items."""
            commands.list_todos()

        @self.typer.command("create")
        def create(
            title: str = typer.Argument(..., help="Title of the todo item"),
            description: str | None = typer.Option(
                None, "--description", "-d", help="Optional todo description"
            ),
        ) -> None:
            """Create a new todo item."""
            commands.create(title, description)

        @self.typer.command("update")
        def update(
            todo_id: int = typer.Argument(..., help="ID of the todo item to update"),
            title: str | None = typer.Option(None, "--title", "-t", help="New title"),
            description: str | None = typer.Option(None, "--description", "-d", help="New description"),
        ) -> None:
            """Update an existing todo item."""
            commands.update(todo_id, title, description)

        @self.typer.command("delete")
        def delete(
            todo_id: int = typer.Argument(..., help="ID of the todo item to delete"),
        ) -> None:
            """Delete a todo item by ID."""
            commands.delete(todo_id)

        @self.typer.command("complete")
        def complete(
            todo_id: int = typer.Argument(..., help="ID of the todo item to mark as completed"),
        ) -> None:
            """Mark a todo item as completed."""
            commands.complete(todo_id)

        @self.typer.command("reopen")
        def reopen(
            todo_id: int = typer.Argument(..., help="ID of the todo item to reopen"),
        ) -> None:
            """Reopen a completed todo item."""
            commands.reopen(todo_id)

        @self.typer.command("shell")
        def shell() -> None:
            """Start an interactive shell for todo commands."""
            TodoShell(self.typer).run()
