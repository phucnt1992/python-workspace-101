from typing import Annotated
from fastapi import Depends
from api.todo.services import TodoService
from infra.db import DbSessionDep

def get_todo_service(db: DbSessionDep) -> TodoService:
    return TodoService(db)

TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
