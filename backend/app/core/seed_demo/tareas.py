"""Una tarea por cada estado del workflow, con un comentario de ejemplo."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comentario_tarea import ComentarioTarea
from app.models.tarea import Tarea
from app.models.user import User


async def seed_tareas(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    admin: User,
    ctx: dict[str, Any],
    usuarios: dict[str, User],
) -> None:
    materias = ctx["materias"]
    coordinador = usuarios["COORDINADOR"]
    profesor = usuarios["PROFESOR"]
    tutor = usuarios["TUTOR"]

    tareas_data = [
        {
            "materia_id": materias["PROG1"].id,
            "asignado_a": profesor.id,
            "asignado_por": coordinador.id,
            "estado": "Pendiente",
            "descripcion": "Revisar actas del primer parcial de Programación I",
        },
        {
            "materia_id": materias["BD1"].id,
            "asignado_a": tutor.id,
            "asignado_por": admin.id,
            "estado": "En progreso",
            "descripcion": "Contactar a los alumnos atrasados en Base de Datos I",
        },
        {
            "materia_id": None,
            "asignado_a": profesor.id,
            "asignado_por": coordinador.id,
            "estado": "Resuelta",
            "descripcion": "Cargar el programa de la materia para el cuatrimestre",
        },
    ]

    existing = await db.execute(
        select(Tarea).where(
            Tarea.tenant_id == tenant_id,
            Tarea.descripcion == tareas_data[0]["descripcion"],
            Tarea.deleted_at.is_(None),
        )
    )
    if existing.unique().scalar_one_or_none() is not None:
        return

    creadas: list[Tarea] = []
    for td in tareas_data:
        tarea = Tarea(tenant_id=tenant_id, contexto_id=None, **td)
        db.add(tarea)
        creadas.append(tarea)
    await db.flush()

    db.add(ComentarioTarea(
        tenant_id=tenant_id,
        tarea_id=creadas[0].id,
        autor_id=coordinador.id,
        texto="Por favor priorizar esta revisión antes del viernes.",
    ))
    await db.flush()
