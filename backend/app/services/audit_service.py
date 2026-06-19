from __future__ import annotations

import uuid
from collections.abc import Callable, Sequence
from datetime import datetime
from functools import wraps

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.audit_log import AuditLogRepository

CALIFICACIONES_IMPORTAR = "CALIFICACIONES_IMPORTAR"
PADRON_CARGAR = "PADRON_CARGAR"
COMUNICACION_ENVIAR = "COMUNICACION_ENVIAR"
ASIGNACION_MODIFICAR = "ASIGNACION_MODIFICAR"
LIQUIDACION_CALCULAR = "LIQUIDACION_CALCULAR"
LIQUIDACION_CERRAR = "LIQUIDACION_CERRAR"
LIQUIDACION_EXPORTAR = "LIQUIDACION_EXPORTAR"
FACTURA_CARGAR = "FACTURA_CARGAR"
FACTURA_ABONAR = "FACTURA_ABONAR"
SALARIO_CONFIGURAR = "SALARIO_CONFIGURAR"
IMPERSONACION_INICIAR = "IMPERSONACION_INICIAR"
IMPERSONACION_FINALIZAR = "IMPERSONACION_FINALIZAR"
ENCUENTRO_CREAR = "ENCUENTRO_CREAR"
ENCUENTRO_EDITAR = "ENCUENTRO_EDITAR"
GUARDIA_CREAR = "GUARDIA_CREAR"
COLOQUIO_CREAR = "COLOQUIO_CREAR"
COLOQUIO_RESERVAR = "COLOQUIO_RESERVAR"
COLOQUIO_CERRAR = "COLOQUIO_CERRAR"
AVISO_PUBLICAR = "AVISO_PUBLICAR"
AVISO_EDITAR = "AVISO_EDITAR"
AVISO_ELIMINAR = "AVISO_ELIMINAR"
TAREA_CREAR = "TAREA_CREAR"
TAREA_EDITAR = "TAREA_EDITAR"
TAREA_COMENTAR = "TAREA_COMENTAR"


class AuditLogService:
    CALIFICACIONES_IMPORTAR = CALIFICACIONES_IMPORTAR
    PADRON_CARGAR = PADRON_CARGAR
    COMUNICACION_ENVIAR = COMUNICACION_ENVIAR
    ASIGNACION_MODIFICAR = ASIGNACION_MODIFICAR
    LIQUIDACION_CALCULAR = LIQUIDACION_CALCULAR
    LIQUIDACION_CERRAR = LIQUIDACION_CERRAR
    LIQUIDACION_EXPORTAR = LIQUIDACION_EXPORTAR
    FACTURA_CARGAR = FACTURA_CARGAR
    FACTURA_ABONAR = FACTURA_ABONAR
    SALARIO_CONFIGURAR = SALARIO_CONFIGURAR
    IMPERSONACION_INICIAR = IMPERSONACION_INICIAR
    IMPERSONACION_FINALIZAR = IMPERSONACION_FINALIZAR
    ENCUENTRO_CREAR = ENCUENTRO_CREAR
    ENCUENTRO_EDITAR = ENCUENTRO_EDITAR
    GUARDIA_CREAR = GUARDIA_CREAR
    COLOQUIO_CREAR = COLOQUIO_CREAR
    COLOQUIO_RESERVAR = COLOQUIO_RESERVAR
    COLOQUIO_CERRAR = COLOQUIO_CERRAR
    AVISO_PUBLICAR = AVISO_PUBLICAR
    AVISO_EDITAR = AVISO_EDITAR
    AVISO_ELIMINAR = AVISO_ELIMINAR
    TAREA_CREAR = TAREA_CREAR
    TAREA_EDITAR = TAREA_EDITAR
    TAREA_COMENTAR = TAREA_COMENTAR

    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = AuditLogRepository(tenant_id=tenant_id)

    async def log(
        self,
        db: AsyncSession,
        *,
        actor_id: uuid.UUID,
        accion: str,
        impersonado_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        detalle: dict | None = None,
        filas_afectadas: int = 0,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        data = {
            "actor_id": actor_id,
            "accion": accion,
        }
        if impersonado_id is not None:
            data["impersonado_id"] = impersonado_id
        if materia_id is not None:
            data["materia_id"] = materia_id
        if detalle is not None:
            data["detalle"] = detalle
        if filas_afectadas != 0:
            data["filas_afectadas"] = filas_afectadas
        if ip is not None:
            data["ip"] = ip
        if user_agent is not None:
            data["user_agent"] = user_agent

        await self._repo.create(db, data)

    async def list(
        self,
        db: AsyncSession,
        *,
        actor_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        accion: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        pagina: int = 1,
        por_pagina: int = 50,
    ) -> tuple[list, int]:
        offset = (pagina - 1) * por_pagina
        items = await self._repo.list(
            db,
            actor_id=actor_id,
            materia_id=materia_id,
            accion=accion,
            desde=desde,
            hasta=hasta,
            offset=offset,
            limit=por_pagina,
        )
        total = await self._repo.count(
            db,
            actor_id=actor_id,
            materia_id=materia_id,
            accion=accion,
            desde=desde,
            hasta=hasta,
        )
        return list(items), total

    async def acciones_por_dia(
        self,
        db: AsyncSession,
        *,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        accion: str | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        return await self._repo.acciones_por_dia(
            db,
            desde=desde,
            hasta=hasta,
            materia_id=materia_id,
            actor_id=actor_id,
            accion=accion,
            materias_ids=materias_ids,
        )

    async def comunicaciones_por_docente(
        self,
        db: AsyncSession,
        *,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        return await self._repo.comunicaciones_por_docente(
            db,
            desde=desde,
            hasta=hasta,
            materia_id=materia_id,
            materias_ids=materias_ids,
        )

    async def interacciones_por_docente_materia(
        self,
        db: AsyncSession,
        *,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        return await self._repo.interacciones_por_docente_materia(
            db,
            desde=desde,
            hasta=hasta,
            materia_id=materia_id,
            actor_id=actor_id,
            materias_ids=materias_ids,
        )

    async def ultimas_acciones(
        self,
        db: AsyncSession,
        *,
        max_resultados: int = 200,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        accion: str | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> Sequence[AuditLog]:
        max_resultados = min(max_resultados, 1000)
        return await self._repo.ultimas_acciones(
            db,
            max_resultados=max_resultados,
            desde=desde,
            hasta=hasta,
            materia_id=materia_id,
            actor_id=actor_id,
            accion=accion,
            materias_ids=materias_ids,
        )


async def log_action(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    actor_id: uuid.UUID,
    accion: str,
    impersonado_id: uuid.UUID | None = None,
    materia_id: uuid.UUID | None = None,
    detalle: dict | None = None,
    filas_afectadas: int = 0,
    ip: str | None = None,
    user_agent: str | None = None,
) -> None:
    svc = AuditLogService(tenant_id=tenant_id)
    await svc.log(
        db,
        actor_id=actor_id,
        accion=accion,
        impersonado_id=impersonado_id,
        materia_id=materia_id,
        detalle=detalle,
        filas_afectadas=filas_afectadas,
        ip=ip,
        user_agent=user_agent,
    )


def audit_log(accion: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            request: Request | None = kwargs.get("request")
            current_user = kwargs.get("current_user")
            db: AsyncSession | None = kwargs.get("db")

            if db is not None and current_user is not None:
                ip = None
                user_agent = None
                if request is not None:
                    ip = request.client.host if request.client else None
                    user_agent = request.headers.get("user-agent")

                impersonator_id = getattr(current_user, "impersonator_id", None)
                if impersonator_id is not None:
                    actor_id = uuid.UUID(impersonator_id)
                    impersonado_id = current_user.id
                else:
                    actor_id = current_user.id
                    impersonado_id = None

                await log_action(
                    db=db,
                    tenant_id=current_user.tenant_id,
                    actor_id=actor_id,
                    accion=accion,
                    impersonado_id=impersonado_id,
                    ip=ip,
                    user_agent=user_agent,
                )

            return result

        return wrapper

    return decorator
