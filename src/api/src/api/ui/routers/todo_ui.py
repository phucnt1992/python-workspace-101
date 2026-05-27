import logging
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from infra.db import DbSessionDep
from infra.settings import get_settings
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from api.todo.dependencies import TodoServiceDep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui", tags=["todo-ui"])

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


async def _render_todo_list(request: Request, service: TodoServiceDep):
    todos = await service.list_all()
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos},
    )


@router.get("/")
@router.get("/todos", include_in_schema=False)
async def get_todo_page(request: Request, service: TodoServiceDep):
    todos = await service.list_all()
    return templates.TemplateResponse(
        request=request,
        name="todo_page.html",
        context={"todos": todos},
    )


@router.get("/list")
@router.get("/todos/list", include_in_schema=False)
async def get_todo_list_partial(request: Request, service: TodoServiceDep):
    return await _render_todo_list(request, service)


@router.post("/create")
@router.post("/todos", include_in_schema=False)
async def create_todo_ui(
    request: Request,
    service: TodoServiceDep,
    title: str = Form(...),
    description: str | None = Form(None),
):
    todo = await service.create(title, description)
    logger.info("todo.created", extra={"todo_id": todo.id, "todo_title": todo.title, "source": "ui"})
    return await _render_todo_list(request, service)


@router.post("/{todo_id}/update")
@router.post("/todos/{todo_id}/update", include_in_schema=False)
async def update_todo_ui(
    todo_id: int,
    request: Request,
    service: TodoServiceDep,
    title: str = Form(...),
    description: str | None = Form(None),
):
    todo = await service.update(todo_id, title=title, description=description)
    logger.info("todo.updated", extra={"todo_id": todo.id, "todo_title": todo.title, "source": "ui"})
    return await _render_todo_list(request, service)


@router.post("/{todo_id}/complete")
@router.post("/todos/{todo_id}/complete", include_in_schema=False)
async def complete_todo_ui(todo_id: int, request: Request, service: TodoServiceDep):
    todo = await service.set_completed(todo_id, True)
    logger.info("todo.completed", extra={"todo_id": todo.id, "source": "ui"})
    return await _render_todo_list(request, service)


@router.post("/{todo_id}/reopen")
@router.post("/todos/{todo_id}/reopen", include_in_schema=False)
async def reopen_todo_ui(todo_id: int, request: Request, service: TodoServiceDep):
    todo = await service.set_completed(todo_id, False)
    logger.info("todo.reopened", extra={"todo_id": todo.id, "source": "ui"})
    return await _render_todo_list(request, service)


@router.post("/{todo_id}/delete")
@router.post("/todos/{todo_id}/delete", include_in_schema=False)
async def delete_todo_ui(todo_id: int, request: Request, service: TodoServiceDep):
    await service.delete(todo_id)
    logger.info("todo.deleted", extra={"todo_id": todo_id, "source": "ui"})
    return await _render_todo_list(request, service)


@router.get("/health")
async def get_health_status_partial(request: Request, db: DbSessionDep):
    liveness_ok = True
    readiness_ok = True

    try:
        _ = get_settings()
    except ValueError:
        liveness_ok = False

    try:
        result = await db.exec(text("SELECT 1;"))  # type: ignore[arg-type]
        if result.first() != (1,):
            readiness_ok = False
    except SQLAlchemyError:
        readiness_ok = False

    return templates.TemplateResponse(
        request=request,
        name="partials/health_status.html",
        context={"liveness_ok": liveness_ok, "readiness_ok": readiness_ok},
    )
