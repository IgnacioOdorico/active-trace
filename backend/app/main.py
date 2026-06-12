from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers.admin import router as admin_router
from app.api.v1.routers.audit import router as audit_router
from app.api.v1.routers.auditoria_panel import router as auditoria_panel_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.estructura import router as estructura_router
from app.api.v1.routers.health import router as health_router
from app.core.config import Settings
from app.core.database import close_db, init_db
from app.core.logging import setup_logging
from app.core.observability import setup_observability
from app.routers.analisis import router as analisis_router
from app.routers.avisos import router as avisos_router
from app.routers.tareas import router as tareas_router
from app.routers.asignaciones import router as asignaciones_router
from app.routers.equipos import router as equipos_router
from app.routers.calificaciones import router as calificaciones_router
from app.routers.coloquios import router as coloquios_router
from app.routers.comunicaciones import router as comunicaciones_router
from app.routers.encuentros import router as encuentros_router
from app.routers.fechas_academicas import router as fechas_academicas_router
from app.routers.programas import router as programas_router
from app.routers.guardias import router as guardias_router
from app.routers.padron import router as padron_router
from app.routers.umbral import router as umbral_router
from app.routers.usuarios import router as usuarios_router
from app.routers.salario_base import router as salario_base_router
from app.routers.salario_plus import router as salario_plus_router
from app.routers.liquidaciones import router as liquidaciones_router
from app.routers.facturas import router as facturas_router

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
app.include_router(auditoria_panel_router)
app.include_router(auth_router)
app.include_router(estructura_router)
app.include_router(usuarios_router)
app.include_router(avisos_router)
app.include_router(tareas_router)
app.include_router(asignaciones_router)
app.include_router(equipos_router)
app.include_router(analisis_router)
app.include_router(calificaciones_router)
app.include_router(coloquios_router)
app.include_router(comunicaciones_router)
app.include_router(encuentros_router)
app.include_router(programas_router)
app.include_router(fechas_academicas_router)
app.include_router(guardias_router)
app.include_router(umbral_router)
app.include_router(padron_router)
app.include_router(salario_base_router)
app.include_router(salario_plus_router)
app.include_router(liquidaciones_router)
app.include_router(facturas_router)
