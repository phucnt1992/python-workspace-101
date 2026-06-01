import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlmodel import select

from api.middleware import HtmxSpanMiddleware
from api.todo.exception_handlers import register_todo_exception_handlers
from api.todo.routers.todos import router as todos_router
from api.ui.routers.todo_ui import router as todo_ui_router
from domain.todo import Todo
from infra.db import DbSessionDep, init_db

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logging.basicConfig(level=logging.INFO)
    await init_db()
    yield


app = FastAPI(title="Todo API", version="1.0.0", description="HTTP API for Todo use cases.", lifespan=lifespan)

FastAPIInstrumentor.instrument_app(app)
register_todo_exception_handlers(app)
app.add_middleware(HtmxSpanMiddleware)

app.include_router(todos_router)
app.include_router(todo_ui_router)


@app.get("/api/_healthz/liveness", tags=["healthz"])
def get_liveness() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/api/_healthz/readiness", tags=["healthz"])
async def get_readiness(db: DbSessionDep) -> JSONResponse:
    try:
        await db.exec(select(Todo).limit(1))
        return JSONResponse({"status": "ok"})
    except Exception:
        _logger.exception("Readiness check failed")
        return JSONResponse(status_code=503, content={"status": "error"})
