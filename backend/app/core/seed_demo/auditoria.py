"""Entradas de audit log de ejemplo, con códigos de acción reales del sistema."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.audit_service import AuditLogService


async def seed_auditoria(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    admin: User,
    ctx: dict[str, Any],
) -> None:
    materias = ctx["materias"]

    existing = await db.execute(
        select(AuditLog).where(
            AuditLog.tenant_id == tenant_id,
            AuditLog.accion == AuditLogService.PADRON_CARGAR,
        )
    )
    if existing.unique().scalars().first() is not None:
        return

    entradas = [
        {
            "actor_id": admin.id,
            "materia_id": materias["PROG1"].id,
            "accion": AuditLogService.PADRON_CARGAR,
            "detalle": {"version": "seed", "filas": 12},
            "filas_afectadas": 12,
        },
        {
            "actor_id": admin.id,
            "materia_id": materias["PROG1"].id,
            "accion": AuditLogService.CALIFICACIONES_IMPORTAR,
            "detalle": {"actividades": ["TP1", "TP2", "Parcial 1", "Parcial 2", "Recuperatorio"]},
            "filas_afectadas": 60,
        },
        {
            "actor_id": admin.id,
            "materia_id": None,
            "accion": AuditLogService.AVISO_PUBLICAR,
            "detalle": {"titulo": "Receso de invierno"},
            "filas_afectadas": 1,
        },
        {
            "actor_id": admin.id,
            "materia_id": materias["MAT1"].id,
            "accion": AuditLogService.GUARDIA_CREAR,
            "detalle": {"dia": "Miércoles", "horario": "14:00-16:00"},
            "filas_afectadas": 1,
        },
    ]

    for entrada in entradas:
        db.add(AuditLog(tenant_id=tenant_id, ip="127.0.0.1", user_agent="seed-script", **entrada))

    await db.flush()
