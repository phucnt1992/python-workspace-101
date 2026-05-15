import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from .get_todo_by_id import get_todo_by_id

_logger = logging.getLogger(__name__)


async def delete_todo(db_session: AsyncSession, todo_id: int) -> bool:
    _logger.debug("Deleting todo", extra={"todo_id": todo_id})
    todo = await get_todo_by_id(db_session, todo_id)
    if todo is None:
        _logger.warning(f"Todo with id={todo_id} not found.")
        return False

    await db_session.delete(todo)
    await db_session.commit()
    return True
