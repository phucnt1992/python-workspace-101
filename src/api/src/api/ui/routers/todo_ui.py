from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/ui", tags=["ui"])

@router.get("/", response_class=HTMLResponse)
@router.get("/todos", response_class=HTMLResponse)
async def index() -> str:
    return "<h1>Todo UI</h1>"
