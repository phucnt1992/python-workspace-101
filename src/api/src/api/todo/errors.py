class TodoError(Exception):
    pass

class TodoNotFoundError(TodoError):
    def __init__(self, todo_id: int) -> None:
        super().__init__(f"Todo {todo_id} not found")
        self.todo_id = todo_id

class InvalidTodoTitleError(TodoError):
    def __init__(self) -> None:
        super().__init__("Title is required")
