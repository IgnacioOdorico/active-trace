from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers.health import router as health_router
from app.core.config import Settings
from app.core.database import close_db, init_db
from app.core.logging import setup_logging
from app.core.observability import setup_observability

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    setup_observability(
        app,
        service_name=settings.OTEL_SERVICE_NAME,
        otlp_endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        enabled=settings.OTEL_ENABLED,
    )
    init_db(settings.DATABASE_URL)
    yield
    await close_db()


app = FastAPI(lifespan=lifespan, title="activia-trace")
app.include_router(health_router, tags=["health"])
