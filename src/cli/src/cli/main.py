import typer

from cli.demo import app as demo_app
from cli.todo import ToDoApp, create_todo_commands

app = typer.Typer(help="Todo management CLI")

app.add_typer(ToDoApp(create_todo_commands()).typer, name="todo")
app.add_typer(demo_app, name="demo")


if __name__ == "__main__":
    app()
