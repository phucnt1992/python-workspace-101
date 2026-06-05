import logging

from domain.todo import Todo
from sqlmodel.ext.asyncio.session import AsyncSession

from .get_todo_by_id import get_todo_by_id

_logger = logging.getLogger(__name__)


async def update_todo(
    db_session: AsyncSession,
    todo_id: int,
    title: str | None = None,
    description: str | None = None,
) -> Todo | None:
    _logger.debug("Updating todo i", extra={"todo_id": todo_id, "title": title, "description": description})

    todo = await get_todo_by_id(db_session, todo_id)
    if todo is None:
        _logger.warning(f"Todo with id={todo_id} was not found.")
        return None

    if title is not None:
        todo.title = title

    if description is not None:
        todo.description = description

    db_session.add(todo)
    await db_session.commit()
    await db_session.refresh(todo)
    return todo
