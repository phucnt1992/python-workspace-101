import logging
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from infra.db import DbSessionDep
from infra.settings import get_settings
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from use_cases.todo import (
    create_todo,
    delete_todo,
    get_todo_list,
    set_todo_completed,
    update_todo,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui", tags=["todo-ui"])

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


async def _render_todo_list(request: Request, db: DbSessionDep):
    todos = list(await get_todo_list(db))
    return templates.TemplateResponse(
        request=request,
        name="partials/todo_list.html",
        context={"todos": todos},
    )


@router.get("/")
@router.get("/todos", include_in_schema=False)
async def get_todo_page(request: Request, db: DbSessionDep):
    todos = list(await get_todo_list(db))
    return templates.TemplateResponse(
        request=request,
        name="todo_page.html",
        context={"todos": todos},
    )


@router.get("/list")
@router.get("/todos/list", include_in_schema=False)
async def get_todo_list_partial(request: Request, db: DbSessionDep):
    return await _render_todo_list(request, db)


@router.post("/create")
@router.post("/todos", include_in_schema=False)
async def create_todo_ui(
    request: Request,
    db: DbSessionDep,
    title: str = Form(...),
    description: str | None = Form(None),
):
    stripped_title = title.strip()
    if not stripped_title:
        logger.warning("todo.create.invalid_title")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title is required")
    todo = await create_todo(db, stripped_title, description)
    logger.info("todo.created", extra={"todo_id": todo.id, "todo_title": todo.title, "source": "ui"})
    return await _render_todo_list(request, db)


@router.post("/{todo_id}/update")
@router.post("/todos/{todo_id}/update", include_in_schema=False)
async def update_todo_ui(
    todo_id: int,
    request: Request,
    db: DbSessionDep,
    title: str = Form(...),
    description: str | None = Form(None),
):
    stripped_title = title.strip()
    if not stripped_title:
        logger.warning("todo.update.invalid_title", extra={"todo_id": todo_id})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title is required")
    todo = await update_todo(db, todo_id, stripped_title, description)
    if todo is None:
        logger.warning("todo.not_found", extra={"todo_id": todo_id, "operation": "update", "source": "ui"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    logger.info("todo.updated", extra={"todo_id": todo.id, "todo_title": todo.title, "source": "ui"})
    return await _render_todo_list(request, db)


@router.post("/{todo_id}/complete")
@router.post("/todos/{todo_id}/complete", include_in_schema=False)
async def complete_todo_ui(todo_id: int, request: Request, db: DbSessionDep):
    todo = await set_todo_completed(db, todo_id, True)
    if todo is None:
        logger.warning("todo.not_found", extra={"todo_id": todo_id, "operation": "complete", "source": "ui"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    logger.info("todo.completed", extra={"todo_id": todo.id, "source": "ui"})
    return await _render_todo_list(request, db)


@router.post("/{todo_id}/reopen")
@router.post("/todos/{todo_id}/reopen", include_in_schema=False)
async def reopen_todo_ui(todo_id: int, request: Request, db: DbSessionDep):
    todo = await set_todo_completed(db, todo_id, False)
    if todo is None:
        logger.warning("todo.not_found", extra={"todo_id": todo_id, "operation": "reopen", "source": "ui"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    logger.info("todo.reopened", extra={"todo_id": todo.id, "source": "ui"})
    return await _render_todo_list(request, db)


@router.post("/{todo_id}/delete")
@router.post("/todos/{todo_id}/delete", include_in_schema=False)
async def delete_todo_ui(todo_id: int, request: Request, db: DbSessionDep):
    deleted = await delete_todo(db, todo_id)
    if not deleted:
        logger.warning("todo.not_found", extra={"todo_id": todo_id, "operation": "delete", "source": "ui"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    logger.info("todo.deleted", extra={"todo_id": todo_id, "source": "ui"})
    return await _render_todo_list(request, db)


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
