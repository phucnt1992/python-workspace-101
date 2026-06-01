import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from api.todo.errors import InvalidTodoTitleError, TodoNotFoundError

_logger = logging.getLogger(__name__)


async def _todo_not_found_handler(request: Request, exc: TodoNotFoundError) -> JSONResponse:
    _logger.warning("Todo not found", extra={"todo_id": exc.todo_id, "path": request.url.path})
    return JSONResponse(status_code=404, content={"detail": "Todo not found"})


async def _invalid_title_handler(request: Request, exc: InvalidTodoTitleError) -> JSONResponse:
    _logger.warning("Invalid todo title", extra={"path": request.url.path})
    return JSONResponse(status_code=422, content={"detail": "Title is required"})


async def _db_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    _logger.error("Database error", extra={"path": request.url.path}, exc_info=exc)
    return JSONResponse(status_code=503, content={"detail": "Database is temporarily unavailable"})


def register_todo_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TodoNotFoundError, _todo_not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidTodoTitleError, _invalid_title_handler)  # type: ignore[arg-type]
    app.add_exception_handler(SQLAlchemyError, _db_error_handler)  # type: ignore[arg-type]
