import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from infra.db import DbSessionDep, dispose_engine, init_db
from infra.settings import get_settings
from infra.telemetry import setup_logging, setup_telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlmodel import select

from api.middleware import HtmxSpanMiddleware
from api.todo.exception_handlers import register_todo_exception_handlers
from api.todo.routers.todos import router as todos_router
from api.ui.routers.todo_ui import router as todo_ui_router
from domain.todo import Todo

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging()
    setup_telemetry(settings.otel_service_name)
    _logger.info("application.startup", extra={"service": settings.otel_service_name})
    await init_db()
    _logger.info("application.ready")
    yield
    _logger.info("application.shutdown")
    await dispose_engine()


app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="HTTP API for Todo use cases.",
    lifespan=lifespan,
    openapi_url="/openapi.json",
    docs_url="/docs",
)
FastAPIInstrumentor().instrument_app(app)
register_todo_exception_handlers(app)
app.add_middleware(HtmxSpanMiddleware)
app.include_router(todos_router)
app.include_router(todo_ui_router)

ui_static_dir = Path(__file__).resolve().parent / "ui" / "static"
app.mount("/ui/static", StaticFiles(directory=str(ui_static_dir)), name="ui-static")


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
