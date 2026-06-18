"""Evaluación (coloquio) con un día disponible, una reserva y un resultado."""

import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluacion import Evaluacion
from app.models.evaluacion_alumno import EvaluacionAlumno
from app.models.evaluacion_dia import EvaluacionDia
from app.models.reserva_evaluacion import ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.user import User


async def seed_coloquios(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    ctx: dict[str, Any],
    usuarios: dict[str, User],
) -> None:
    materias = ctx["materias"]
    cohorte = ctx["cohorte"]
    alumno = usuarios["ALUMNO"]

    existing = await db.execute(
        select(Evaluacion).where(
            Evaluacion.tenant_id == tenant_id,
            Evaluacion.materia_id == materias["PROG1"].id,
            Evaluacion.tipo == "Coloquio",
            Evaluacion.deleted_at.is_(None),
        )
    )
    evaluacion = existing.unique().scalar_one_or_none()
    if evaluacion is None:
        evaluacion = Evaluacion(
            tenant_id=tenant_id,
            materia_id=materias["PROG1"].id,
            cohorte_id=cohorte.id,
            tipo="Coloquio",
            instancia="Coloquio Final 2026",
            dias_disponibles=2,
            estado="Activa",
        )
        db.add(evaluacion)
        await db.flush()

    existing_dia = await db.execute(
        select(EvaluacionDia).where(
            EvaluacionDia.tenant_id == tenant_id,
            EvaluacionDia.evaluacion_id == evaluacion.id,
            EvaluacionDia.deleted_at.is_(None),
        )
    )
    dia = existing_dia.unique().scalar_one_or_none()
    if dia is None:
        dia = EvaluacionDia(
            tenant_id=tenant_id,
            evaluacion_id=evaluacion.id,
            fecha=date(2026, 7, 10),
            cupo_maximo=5,
            cupos_restantes=4,
        )
        db.add(dia)
        await db.flush()

    existing_ea = await db.execute(
        select(EvaluacionAlumno).where(
            EvaluacionAlumno.tenant_id == tenant_id,
            EvaluacionAlumno.evaluacion_id == evaluacion.id,
            EvaluacionAlumno.alumno_id == alumno.id,
        )
    )
    if existing_ea.unique().scalar_one_or_none() is None:
        db.add(EvaluacionAlumno(
            tenant_id=tenant_id,
            evaluacion_id=evaluacion.id,
            alumno_id=alumno.id,
        ))

    existing_reserva = await db.execute(
        select(ReservaEvaluacion).where(
            ReservaEvaluacion.tenant_id == tenant_id,
            ReservaEvaluacion.evaluacion_dia_id == dia.id,
            ReservaEvaluacion.alumno_id == alumno.id,
            ReservaEvaluacion.deleted_at.is_(None),
        )
    )
    if existing_reserva.unique().scalar_one_or_none() is None:
        db.add(ReservaEvaluacion(
            tenant_id=tenant_id,
            evaluacion_dia_id=dia.id,
            alumno_id=alumno.id,
            estado="Activa",
        ))

    existing_resultado = await db.execute(
        select(ResultadoEvaluacion).where(
            ResultadoEvaluacion.tenant_id == tenant_id,
            ResultadoEvaluacion.evaluacion_id == evaluacion.id,
            ResultadoEvaluacion.alumno_id == alumno.id,
        )
    )
    if existing_resultado.unique().scalar_one_or_none() is None:
        db.add(ResultadoEvaluacion(
            tenant_id=tenant_id,
            evaluacion_id=evaluacion.id,
            alumno_id=alumno.id,
            nota_final="Aprobado",
        ))

    await db.flush()
