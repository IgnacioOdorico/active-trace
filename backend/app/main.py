from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers.admin import router as admin_router
from app.api.v1.routers.audit import router as audit_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.estructura import router as estructura_router
from app.api.v1.routers.health import router as health_router
from app.core.config import Settings
from app.core.database import close_db, init_db
from app.core.logging import setup_logging
from app.core.observability import setup_observability
from app.routers.asignaciones import router as asignaciones_router
from app.routers.usuarios import router as usuarios_router

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
app.include_router(admin_router)
app.include_router(audit_router)
app.include_router(auth_router)
app.include_router(estructura_router)
app.include_router(usuarios_router)
app.include_router(asignaciones_router)
