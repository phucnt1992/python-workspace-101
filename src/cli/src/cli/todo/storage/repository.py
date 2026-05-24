from typing import Protocol

from domain.todo import Todo
from sqlmodel.ext.asyncio.session import AsyncSession
from use_cases.todo import (
    create_todo,
    delete_todo,
    get_todo_list,
    set_todo_completed,
    update_todo,
)


class TodoRepository(Protocol):
    async def list_all(self, session: AsyncSession) -> list[Todo]: ...

    async def create(self, session: AsyncSession, title: str, description: str | None) -> Todo: ...

    async def update(
        self,
        session: AsyncSession,
        todo_id: int,
        *,
        title: str | None,
        description: str | None,
    ) -> Todo | None: ...

    async def delete(self, session: AsyncSession, todo_id: int) -> bool: ...

    async def set_completed(self, session: AsyncSession, todo_id: int, completed: bool) -> Todo | None: ...


class SqlTodoRepository:
    async def list_all(self, session: AsyncSession) -> list[Todo]:
        result = await get_todo_list(session)
        return list(result)

    async def create(self, session: AsyncSession, title: str, description: str | None) -> Todo:
        return await create_todo(session, title, description)

    async def update(
        self,
        session: AsyncSession,
        todo_id: int,
        *,
        title: str | None,
        description: str | None,
    ) -> Todo | None:
        return await update_todo(session, todo_id, title=title, description=description)

    async def delete(self, session: AsyncSession, todo_id: int) -> bool:
        return await delete_todo(session, todo_id)

    async def set_completed(self, session: AsyncSession, todo_id: int, completed: bool) -> Todo | None:
        return await set_todo_completed(session, todo_id, completed)
