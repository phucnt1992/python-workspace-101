from domain.todo import Todo


class TodoFormatter:
    def format(self, todo: Todo) -> str:
        status = "x" if todo.completed else " "
        description = f" - {todo.description}" if todo.description else ""
        return f"{todo.id}. [{status}] {todo.title}{description}"
