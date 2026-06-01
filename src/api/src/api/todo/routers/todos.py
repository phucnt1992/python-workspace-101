import logging

from fastapi import APIRouter, Response

from api.todo.dependencies import TodoServiceDep
from api.todo.mappers import TodoMapper
from api.todo.schemas.todo import TodoCreateRequest, TodoListResponse, TodoResponse, TodoUpdateRequest

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=TodoListResponse)
async def list_todos(service: TodoServiceDep, page: int = 1, page_size: int = 10) -> TodoListResponse:
    return await service.list_paginated(page, page_size)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, service: TodoServiceDep) -> TodoResponse:
    todo = await service.get_by_id(todo_id)
    return TodoMapper.to_response(todo)


@router.post("", response_model=TodoResponse, status_code=201)
async def create_todo(body: TodoCreateRequest, service: TodoServiceDep) -> TodoResponse:
    todo = await service.create(body.title, body.description)
    _logger.info("Created todo", extra={"todo_id": todo.id, "title": todo.title})
    return TodoMapper.to_response(todo)


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, body: TodoUpdateRequest, service: TodoServiceDep) -> TodoResponse:
    todo = await service.update(todo_id, title=body.title, description=body.description)
    _logger.info("Updated todo", extra={"todo_id": todo.id})
    return TodoMapper.to_response(todo)


@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(todo_id: int, service: TodoServiceDep) -> TodoResponse:
    todo = await service.set_completed(todo_id, completed=True)
    return TodoMapper.to_response(todo)


@router.post("/{todo_id}/reopen", response_model=TodoResponse)
async def reopen_todo(todo_id: int, service: TodoServiceDep) -> TodoResponse:
    todo = await service.set_completed(todo_id, completed=False)
    return TodoMapper.to_response(todo)


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(todo_id: int, service: TodoServiceDep) -> Response:
    await service.delete(todo_id)
    _logger.info("Deleted todo", extra={"todo_id": todo_id})
    return Response(status_code=204)
