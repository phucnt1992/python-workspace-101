from domain.todo import Todo
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_todo_by_id(db_session: AsyncSession, todo_id: int) -> Todo | None:
    return await db_session.get(Todo, todo_id)
