from domain.todo import Todo
from api.todo.schemas.todo import TodoListResponse, TodoResponse

class TodoMapper:
    @staticmethod
    def to_response(todo: Todo) -> TodoResponse:
        return TodoResponse.model_validate(todo, from_attributes=True)

    @staticmethod
    def to_list_response(
        todos: list[Todo],
        *,
        page: int,
        page_size: int,
        total: int,
    ) -> TodoListResponse:
        return TodoListResponse(
            items=[TodoMapper.to_response(todo) for todo in todos],
            total=total,
            page=page,
            page_size=page_size,
        )
