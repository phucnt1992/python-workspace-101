from pydantic import BaseModel, Field

class TodoCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None

class TodoUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool

class TodoListResponse(BaseModel):
    items: list[TodoResponse]
    total: int
    page: int
    page_size: int
