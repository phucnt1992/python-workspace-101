import logging
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from api.todo.errors import InvalidTodoTitleError, TodoNotFoundError

logger = logging.getLogger(__name__)

_UI_TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "ui" / "templates"
_templates = Jinja2Templates(directory=str(_UI_TEMPLATES_DIR))


def _request_source(request: Request) -> str:
    return "api" if request.url.path.startswith("/api/") else "ui"


def _wants_html(request: Request) -> bool:
    return request.url.path.startswith("/ui/")


def _html_error_response(
    request: Request,
    *,
    message: str,
    status_code: int,
) -> Response:
    return _templates.TemplateResponse(
        request=request,
        name="partials/error_alert.html",
        context={"message": message},
        status_code=status_code,
    )


def _json_error_response(*, detail: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def handle_todo_not_found(_request: Request, exc: TodoNotFoundError) -> Response:
    source = _request_source(_request)
    logger.warning(
        "todo.not_found",
        extra={"todo_id": exc.todo_id, "source": source, "path": _request.url.path},
    )
    if _wants_html(_request):
        return _html_error_response(_request, message="Todo not found", status_code=status.HTTP_404_NOT_FOUND)
    return _json_error_response(detail="Todo not found", status_code=status.HTTP_404_NOT_FOUND)


async def handle_invalid_todo_title(_request: Request, _exc: InvalidTodoTitleError) -> Response:
    source = _request_source(_request)
    logger.warning("todo.invalid_title", extra={"source": source, "path": _request.url.path})
    if _wants_html(_request):
        return _html_error_response(
            _request,
            message="Title is required",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    return _json_error_response(detail="Title is required", status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


async def handle_database_error(_request: Request, exc: SQLAlchemyError) -> Response:
    source = _request_source(_request)
    logger.exception("database.error", extra={"source": source, "path": _request.url.path})
    message = "Database is temporarily unavailable"
    if _wants_html(_request):
        return _html_error_response(_request, message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return _json_error_response(detail=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


def register_todo_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TodoNotFoundError, handle_todo_not_found)
    app.add_exception_handler(InvalidTodoTitleError, handle_invalid_todo_title)
    app.add_exception_handler(SQLAlchemyError, handle_database_error)
