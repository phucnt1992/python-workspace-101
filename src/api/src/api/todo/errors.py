class TodoError(Exception):
    """Base class for todo application errors."""


class TodoNotFoundError(TodoError):
    def __init__(self, todo_id: int) -> None:
        self.todo_id = todo_id
        super().__init__(f"Todo {todo_id} not found")


class InvalidTodoTitleError(TodoError):
    """Raised when a todo title is missing or whitespace-only after normalization."""
