from domain.todo import Todo
from sqlmodel.ext.asyncio.session import AsyncSession
from use_cases.todo import (
    create_todo,
    delete_todo,
    get_todo_by_id,
    get_todo_list,
    set_todo_completed,
    update_todo,
)

from api.todo.errors import InvalidTodoTitleError, TodoNotFoundError
from api.todo.mappers import TodoMapper
from api.todo.schemas.todo import TodoListResponse


class TodoService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @staticmethod
    def _normalize_title(title: str) -> str:
        stripped = title.strip()
        if not stripped:
            raise InvalidTodoTitleError()
        return stripped

    async def list_paginated(self, page: int, page_size: int) -> TodoListResponse:
        todos = list(await get_todo_list(self._db))
        total = len(todos)
        start = (page - 1) * page_size
        end = start + page_size
        return TodoMapper.to_list_response(
            todos[start:end],
            page=page,
            page_size=page_size,
            total=total,
        )

    async def list_all(self) -> list[Todo]:
        return list(await get_todo_list(self._db))

    async def get_by_id(self, todo_id: int) -> Todo:
        todo = await get_todo_by_id(self._db, todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    async def create(self, title: str, description: str | None = None) -> Todo:
        normalized_title = self._normalize_title(title)
        return await create_todo(self._db, normalized_title, description)

    async def update(
        self,
        todo_id: int,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> Todo:
        normalized_title = self._normalize_title(title) if title is not None else None
        todo = await update_todo(self._db, todo_id, normalized_title, description)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    async def set_completed(self, todo_id: int, completed: bool) -> Todo:
        todo = await set_todo_completed(self._db, todo_id, completed)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    async def delete(self, todo_id: int) -> None:
        deleted = await delete_todo(self._db, todo_id)
        if not deleted:
            raise TodoNotFoundError(todo_id)
