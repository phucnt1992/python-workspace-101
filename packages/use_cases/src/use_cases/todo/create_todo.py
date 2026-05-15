from domain.todo import Todo
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_todo(db_session: AsyncSession, title: str, description: str | None = None) -> Todo:
    todo = Todo(title=title, description=description)
    db_session.add(todo)
    await db_session.commit()
    await db_session.refresh(todo)
    return todo
