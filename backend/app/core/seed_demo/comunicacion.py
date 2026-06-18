"""Avisos (con acknowledgment) y comunicaciones en distintos estados."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.aviso import Aviso
from app.models.comunicacion import Comunicacion
from app.models.user import User


async def seed_comunicacion(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    admin: User,
    ctx: dict[str, Any],
    now: datetime,
) -> None:
    materias = ctx["materias"]

    existing_aviso = await db.execute(
        select(Aviso).where(
            Aviso.tenant_id == tenant_id,
            Aviso.titulo == "Receso de invierno",
            Aviso.deleted_at.is_(None),
        )
    )
    aviso = existing_aviso.unique().scalar_one_or_none()
    if aviso is None:
        aviso = Aviso(
            tenant_id=tenant_id,
            alcance="Global",
            materia_id=None,
            cohorte_id=None,
            rol_destino=None,
            severidad="Info",
            titulo="Receso de invierno",
            cuerpo="Las clases se retoman el 3 de agosto. Las entregas con vencimiento durante el receso se reprograman automáticamente.",
            inicio_en=now - timedelta(days=1),
            fin_en=now + timedelta(days=30),
            orden=1,
            activo=True,
            requiere_ack=True,
        )
        db.add(aviso)
        await db.flush()

        db.add(AcknowledgmentAviso(
            tenant_id=tenant_id,
            aviso_id=aviso.id,
            usuario_id=admin.id,
            confirmado_at=now,
        ))

    existing_aviso_materia = await db.execute(
        select(Aviso).where(
            Aviso.tenant_id == tenant_id,
            Aviso.titulo == "Cambio de horario de consulta",
            Aviso.deleted_at.is_(None),
        )
    )
    if existing_aviso_materia.unique().scalar_one_or_none() is None:
        db.add(Aviso(
            tenant_id=tenant_id,
            alcance="PorMateria",
            materia_id=materias["PROG1"].id,
            cohorte_id=None,
            rol_destino=None,
            severidad="Advertencia",
            titulo="Cambio de horario de consulta",
            cuerpo="La consulta semanal de Programación I se mueve de los martes a los jueves a partir de la próxima semana.",
            inicio_en=now,
            fin_en=now + timedelta(days=14),
            orden=2,
            activo=True,
            requiere_ack=False,
        ))

    destinatario_email = "lautaro.martinez@example.com"

    comunicaciones_data = [
        {
            "destinatario": destinatario_email,
            "asunto": "Recordatorio: Parcial 1 de Programación I",
            "cuerpo": "Te recordamos que el Parcial 1 es el próximo lunes a las 18:00.",
            "estado": "Nueva",
            "lote_id": None,
            "intentos": 0,
            "error_msg": None,
            "enviado_at": None,
        },
        {
            "destinatario": destinatario_email,
            "asunto": "Confirmación de entrega recibida",
            "cuerpo": "Recibimos tu entrega de TP1. Te avisamos cuando esté corregida.",
            "estado": "Enviado",
            "lote_id": uuid.uuid4(),
            "intentos": 1,
            "error_msg": None,
            "enviado_at": now - timedelta(hours=2),
        },
        {
            "destinatario": "direccion-invalida@@example",
            "asunto": "Aviso de atraso",
            "cuerpo": "Notamos que tenés actividades pendientes en Base de Datos I.",
            "estado": "Error",
            "lote_id": None,
            "intentos": 3,
            "error_msg": "SMTP rechazó el destinatario: dirección malformada",
            "enviado_at": None,
        },
        {
            "destinatario": destinatario_email,
            "asunto": "Cambio de aula para el coloquio",
            "cuerpo": "El coloquio final se traslada al aula virtual 2.",
            "estado": "Cancelado",
            "lote_id": None,
            "intentos": 0,
            "error_msg": None,
            "enviado_at": None,
        },
    ]

    existing_count = await db.execute(
        select(Comunicacion).where(
            Comunicacion.tenant_id == tenant_id,
            Comunicacion.materia_id == materias["PROG1"].id,
            Comunicacion.deleted_at.is_(None),
        )
    )
    if not existing_count.unique().scalars().all():
        for cd in comunicaciones_data:
            db.add(Comunicacion(
                tenant_id=tenant_id,
                enviado_por=admin.id,
                materia_id=materias["PROG1"].id,
                **cd,
            ))
        await db.flush()
