from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from domain.todo import Todo


async def count_todos(db_session: AsyncSession) -> int:
    result = await db_session.exec(select(func.count()).select_from(Todo))
    return result.one()
