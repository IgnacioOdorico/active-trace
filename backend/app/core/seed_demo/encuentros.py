"""Slots de encuentro recurrentes, una instancia concreta y una guardia."""

import uuid
from datetime import date, time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardia import Guardia
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import SlotEncuentro


async def seed_encuentros(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    ctx: dict[str, Any],
    asignaciones_extra: dict[str, uuid.UUID],
) -> None:
    materias = ctx["materias"]
    carreras = ctx["carreras"]
    cohorte = ctx["cohorte"]
    asignaciones = ctx["asignaciones"]

    existing_slot = await db.execute(
        select(SlotEncuentro).where(
            SlotEncuentro.tenant_id == tenant_id,
            SlotEncuentro.materia_id == materias["PROG1"].id,
            SlotEncuentro.deleted_at.is_(None),
        )
    )
    slot = existing_slot.unique().scalar_one_or_none()
    if slot is None:
        slot = SlotEncuentro(
            tenant_id=tenant_id,
            asignacion_id=asignaciones["PROG1"],
            materia_id=materias["PROG1"].id,
            titulo="Consulta semanal Programación I",
            hora=time(18, 0),
            dia_semana="Martes",
            fecha_inicio=date(2026, 3, 3),
            cant_semanas=20,
            fecha_unica=None,
            meet_url="https://meet.example.com/prog1-consulta",
            vig_desde=date(2026, 3, 1),
            vig_hasta=date(2026, 12, 31),
        )
        db.add(slot)
        await db.flush()

    existing_instancia = await db.execute(
        select(InstanciaEncuentro).where(
            InstanciaEncuentro.tenant_id == tenant_id,
            InstanciaEncuentro.materia_id == materias["PROG1"].id,
            InstanciaEncuentro.deleted_at.is_(None),
        )
    )
    if existing_instancia.unique().scalar_one_or_none() is None:
        db.add(InstanciaEncuentro(
            tenant_id=tenant_id,
            slot_id=slot.id,
            materia_id=materias["PROG1"].id,
            fecha=date(2026, 6, 23),
            hora=time(18, 0),
            titulo="Consulta semanal Programación I",
            estado="Realizado",
            meet_url="https://meet.example.com/prog1-consulta",
            video_url="https://example.com/grabaciones/prog1-2026-06-23.mp4",
            comentario="Repasamos recursividad y se resolvieron dudas del TP2.",
        ))

    guardia_asignacion_id = asignaciones_extra.get("TUTOR", asignaciones["MAT1"])
    existing_guardia = await db.execute(
        select(Guardia).where(
            Guardia.tenant_id == tenant_id,
            Guardia.materia_id == materias["MAT1"].id,
            Guardia.deleted_at.is_(None),
        )
    )
    if existing_guardia.unique().scalar_one_or_none() is None:
        db.add(Guardia(
            tenant_id=tenant_id,
            asignacion_id=guardia_asignacion_id,
            materia_id=materias["MAT1"].id,
            carrera_id=carreras["TUP"].id,
            cohorte_id=cohorte.id,
            dia="Miércoles",
            horario="14:00-16:00",
            estado="Pendiente",
            comentarios="Guardia de consulta para alumnos con dificultades en álgebra.",
        ))

    await db.flush()
