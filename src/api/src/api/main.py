import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from infra.db import DbSessionDep, dispose_engine, init_db
from infra.settings import get_settings
from infra.telemetry import setup_logging, setup_telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlalchemy.sql import text

from api.middleware import HtmxSpanMiddleware
from api.todo.exception_handlers import register_todo_exception_handlers
from api.todo.routers.todos import router as todos_router
from api.ui.routers.todo_ui import router as todo_ui_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    setup_logging()
    setup_telemetry(settings.otel_service_name)
    logger.info("application.startup", extra={"service": settings.otel_service_name})
    await init_db()
    logger.info("application.ready")
    yield
    logger.info("application.shutdown")
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
async def get_liveness_status() -> dict[str, str]:
    _ = get_settings()
    return {"status": "ok"}


@app.get("/api/_healthz/readiness", tags=["healthz"])
async def get_readiness_status(db: DbSessionDep) -> dict[str, str]:
    result = await db.exec(text("SELECT 1;"))  # type: ignore[arg-type]
    if result.first() != (1,):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"status": "error"})
    return {"status": "ok"}
