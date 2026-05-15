from typing import Sequence

from domain.todo import Todo
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_todo_list(db_session: AsyncSession) -> Sequence[Todo]:
    statement = select(Todo)
    result = await db_session.exec(statement)
    return result.all()
