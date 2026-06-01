from typing import Sequence

from domain.todo import Todo
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_todo_list(
    db_session: AsyncSession,
    offset: int = 0,
    limit: int | None = None,
) -> Sequence[Todo]:
    statement = select(Todo).offset(offset)
    if limit is not None:
        statement = statement.limit(limit)
    result = await db_session.exec(statement)
    return result.all()
