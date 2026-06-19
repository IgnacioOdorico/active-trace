"""Fecha académica y programa de materia de ejemplo."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fecha_academica import FechaAcademica
from app.models.programa_materia import ProgramaMateria


async def seed_estructura(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    ctx: dict[str, Any],
    now: datetime,
) -> None:
    materias = ctx["materias"]
    carreras = ctx["carreras"]
    cohorte = ctx["cohorte"]

    existing_fecha = await db.execute(
        select(FechaAcademica).where(
            FechaAcademica.tenant_id == tenant_id,
            FechaAcademica.materia_id == materias["PROG1"].id,
            FechaAcademica.deleted_at.is_(None),
        )
    )
    if existing_fecha.unique().scalar_one_or_none() is None:
        db.add(FechaAcademica(
            tenant_id=tenant_id,
            materia_id=materias["PROG1"].id,
            cohorte_id=cohorte.id,
            tipo="Parcial",
            numero=1,
            periodo="2026-1C",
            fecha=date(2026, 5, 15),
            titulo="Primer Parcial Programación I",
        ))

    existing_programa = await db.execute(
        select(ProgramaMateria).where(
            ProgramaMateria.tenant_id == tenant_id,
            ProgramaMateria.materia_id == materias["PROG1"].id,
            ProgramaMateria.deleted_at.is_(None),
        )
    )
    if existing_programa.unique().scalar_one_or_none() is None:
        db.add(ProgramaMateria(
            tenant_id=tenant_id,
            materia_id=materias["PROG1"].id,
            carrera_id=carreras["TUP"].id,
            cohorte_id=cohorte.id,
            titulo="Programa Programación I - 2026",
            referencia_archivo="programas/prog1_2026.pdf",
            cargado_at=now,
        ))

    await db.flush()
