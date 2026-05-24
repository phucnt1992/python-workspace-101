from cli.todo.application import TodoCommands
from cli.todo.storage import SqlTodoRepository, TodoSessionRunner
from cli.todo.presentation import TodoFormatter, TyperTodoPresenter


def create_todo_commands() -> TodoCommands:
    return TodoCommands(
        runner=TodoSessionRunner(),
        repository=SqlTodoRepository(),
        presenter=TyperTodoPresenter(TodoFormatter()),
    )
