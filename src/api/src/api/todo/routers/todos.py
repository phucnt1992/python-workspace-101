import logging

from fastapi import APIRouter, HTTPException, Query, status
from infra.db import DbSessionDep
from use_cases.todo import (
    create_todo,
    delete_todo,
    get_todo_by_id,
    get_todo_list,
    set_todo_completed,
    update_todo,
)

from api.todo.schemas.todo import TodoCreateRequest, TodoListResponse, TodoResponse, TodoUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=TodoListResponse)
async def list_todos(
    db: DbSessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> TodoListResponse:
    todos = list(await get_todo_list(db))
    total = len(todos)
    start = (page - 1) * page_size
    end = start + page_size
    paged_todos = todos[start:end]
    logger.debug("todo.list", extra={"page": page, "page_size": page_size, "total": total})
    return TodoListResponse(
        items=[TodoResponse.model_validate(todo, from_attributes=True) for todo in paged_todos],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, db: DbSessionDep) -> TodoResponse:
    raise NotImplementedError("Get single todo endpoint not implemented yet")


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo_endpoint(payload: TodoCreateRequest, db: DbSessionDep) -> TodoResponse:
    raise NotImplementedError("Create todo endpoint not implemented yet")


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo_endpoint(todo_id: int, payload: TodoUpdateRequest, db: DbSessionDep) -> TodoResponse:
    raise NotImplementedError("Update todo endpoint not implemented yet")


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_endpoint(todo_id: int, db: DbSessionDep) -> None:
    raise NotImplementedError("Delete todo endpoint not implemented yet")


@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(todo_id: int, db: DbSessionDep) -> TodoResponse:
    raise NotImplementedError("Complete todo endpoint not implemented yet")


@router.post("/{todo_id}/reopen", response_model=TodoResponse)
async def reopen_todo(todo_id: int, db: DbSessionDep) -> TodoResponse:
    raise NotImplementedError("Reopen todo endpoint not implemented yet")
