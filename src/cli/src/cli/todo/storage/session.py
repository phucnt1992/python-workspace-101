import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from infra.db import get_session_context, init_db
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T")


class TodoSessionRunner:
    def run(self, operation: Callable[[AsyncSession], Awaitable[T]]) -> T:
        return asyncio.run(self._execute(operation))

    async def _execute(self, operation: Callable[[AsyncSession], Awaitable[T]]) -> T:
        await init_db()
        async with get_session_context() as session:
            return await operation(session)
