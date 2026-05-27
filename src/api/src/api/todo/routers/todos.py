import logging

from fastapi import APIRouter, Query, status

from api.todo.dependencies import TodoServiceDep
from api.todo.mappers import TodoMapper
from api.todo.schemas.todo import TodoCreateRequest, TodoListResponse, TodoResponse, TodoUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=TodoListResponse)
async def list_todos(
    service: TodoServiceDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> TodoListResponse:
    result = await service.list_paginated(page, page_size)
    logger.debug("todo.list", extra={"page": page, "page_size": page_size, "total": result.total})
    return result


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, service: TodoServiceDep) -> TodoResponse:
    todo = await service.get_by_id(todo_id)
    return TodoMapper.to_response(todo)


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo_endpoint(payload: TodoCreateRequest, service: TodoServiceDep) -> TodoResponse:
    todo = await service.create(payload.title, payload.description)
    logger.info("todo.created", extra={"todo_id": todo.id, "todo_title": todo.title, "source": "api"})
    return TodoMapper.to_response(todo)


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo_endpoint(
    todo_id: int,
    payload: TodoUpdateRequest,
    service: TodoServiceDep,
) -> TodoResponse:
    todo = await service.update(todo_id, title=payload.title, description=payload.description)
    logger.info("todo.updated", extra={"todo_id": todo.id, "todo_title": todo.title, "source": "api"})
    return TodoMapper.to_response(todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_endpoint(todo_id: int, service: TodoServiceDep) -> None:
    await service.delete(todo_id)
    logger.info("todo.deleted", extra={"todo_id": todo_id, "source": "api"})


@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(todo_id: int, service: TodoServiceDep) -> TodoResponse:
    todo = await service.set_completed(todo_id, True)
    logger.info("todo.completed", extra={"todo_id": todo.id, "source": "api"})
    return TodoMapper.to_response(todo)


@router.post("/{todo_id}/reopen", response_model=TodoResponse)
async def reopen_todo(todo_id: int, service: TodoServiceDep) -> TodoResponse:
    todo = await service.set_completed(todo_id, False)
    logger.info("todo.reopened", extra={"todo_id": todo.id, "source": "api"})
    return TodoMapper.to_response(todo)
