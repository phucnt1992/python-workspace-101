from domain.todo import Todo
from sqlmodel.ext.asyncio.session import AsyncSession

from .get_todo_by_id import get_todo_by_id


async def set_todo_completed(db_session: AsyncSession, todo_id: int, completed: bool) -> Todo | None:
    todo = await get_todo_by_id(db_session, todo_id)
    if todo is None:
        return None

    todo.completed = completed
    db_session.add(todo)
    await db_session.commit()
    await db_session.refresh(todo)
    return todo
