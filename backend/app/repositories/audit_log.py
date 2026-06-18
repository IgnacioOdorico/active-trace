from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime, date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.materia import Materia
from app.models.user import User, nombre_completo_usuario


class AuditLogRepository:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._model = AuditLog
        self._tenant_id = tenant_id

    async def create(self, session: AsyncSession, data: dict) -> AuditLog:
        data["tenant_id"] = self._tenant_id
        instance = self._model(**data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def get(self, session: AsyncSession, id: uuid.UUID) -> AuditLog | None:
        query = select(self._model).where(
            self._model.id == id,
            self._model.tenant_id == self._tenant_id,
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        *,
        actor_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        accion: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[AuditLog]:
        query = (
            select(self._model)
            .where(self._model.tenant_id == self._tenant_id)
            .order_by(self._model.fecha_hora.desc())
        )
        if actor_id is not None:
            query = query.where(self._model.actor_id == actor_id)
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if accion is not None:
            query = query.where(self._model.accion == accion)
        if desde is not None:
            query = query.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            query = query.where(self._model.fecha_hora <= hasta)
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def count(
        self,
        session: AsyncSession,
        *,
        actor_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        accion: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> int:
        query = (
            select(func.count())
            .select_from(self._model)
            .where(self._model.tenant_id == self._tenant_id)
        )
        if actor_id is not None:
            query = query.where(self._model.actor_id == actor_id)
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if accion is not None:
            query = query.where(self._model.accion == accion)
        if desde is not None:
            query = query.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            query = query.where(self._model.fecha_hora <= hasta)
        result = await session.execute(query)
        return result.scalar_one()

    async def acciones_por_dia(
        self,
        session: AsyncSession,
        *,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        accion: str | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        query = (
            select(
                func.date(self._model.fecha_hora).label("fecha"),
                func.count().label("total"),
            )
            .where(self._model.tenant_id == self._tenant_id)
            .group_by(func.date(self._model.fecha_hora))
            .order_by(func.date(self._model.fecha_hora))
        )
        if desde is not None:
            query = query.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            query = query.where(self._model.fecha_hora <= hasta)
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if actor_id is not None:
            query = query.where(self._model.actor_id == actor_id)
        if accion is not None:
            query = query.where(self._model.accion == accion)
        if materias_ids is not None:
            query = query.where(self._model.materia_id.in_(materias_ids))
        result = await session.execute(query)
        rows = result.all()
        return [{"fecha": row.fecha, "total": row.total} for row in rows]

    async def comunicaciones_por_docente(
        self,
        session: AsyncSession,
        *,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        query = (
            select(
                self._model.actor_id,
                self._model.accion,
                func.count().label("total"),
                User.nombre,
                User.apellidos,
                User.email,
            )
            .join(User, User.id == self._model.actor_id)
            .where(self._model.tenant_id == self._tenant_id)
            .where(self._model.accion.like("COMUNICACION_%"))
            .group_by(
                self._model.actor_id, self._model.accion,
                User.nombre, User.apellidos, User.email,
            )
        )
        if desde is not None:
            query = query.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            query = query.where(self._model.fecha_hora <= hasta)
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if materias_ids is not None:
            query = query.where(self._model.materia_id.in_(materias_ids))
        result = await session.execute(query)
        rows = result.all()
        grouped: dict[uuid.UUID, dict] = {}
        for row in rows:
            aid = row.actor_id
            if aid not in grouped:
                grouped[aid] = {
                    "docente_id": str(aid),
                    "docente_nombre": nombre_completo_usuario(row.nombre, row.apellidos, row.email),
                    "pendiente": 0,
                    "enviando": 0,
                    "enviado": 0,
                    "fallido": 0,
                    "cancelado": 0,
                }
            acc = row.accion.upper()
            if "ENVIAR" in acc or "ENVIADO" in acc:
                grouped[aid]["enviado"] += row.total
            elif "PENDIENTE" in acc:
                grouped[aid]["pendiente"] += row.total
            elif "ENVIANDO" in acc or "PROCESANDO" in acc:
                grouped[aid]["enviando"] += row.total
            elif "FALLIDO" in acc or "ERROR" in acc:
                grouped[aid]["fallido"] += row.total
            elif "CANCEL" in acc:
                grouped[aid]["cancelado"] += row.total
            else:
                grouped[aid]["enviado"] += row.total
        return list(grouped.values())

    async def interacciones_por_docente_materia(
        self,
        session: AsyncSession,
        *,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        query = (
            select(
                self._model.actor_id,
                self._model.materia_id,
                self._model.accion,
                func.count().label("cnt"),
                User.nombre,
                User.apellidos,
                User.email,
                Materia.nombre.label("materia_nombre"),
            )
            .join(User, User.id == self._model.actor_id)
            .outerjoin(Materia, Materia.id == self._model.materia_id)
            .where(self._model.tenant_id == self._tenant_id)
            .group_by(
                self._model.actor_id, self._model.materia_id, self._model.accion,
                User.nombre, User.apellidos, User.email, Materia.nombre,
            )
        )
        if desde is not None:
            query = query.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            query = query.where(self._model.fecha_hora <= hasta)
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if actor_id is not None:
            query = query.where(self._model.actor_id == actor_id)
        if materias_ids is not None:
            query = query.where(self._model.materia_id.in_(materias_ids))
        result = await session.execute(query)
        rows = result.all()
        grouped: dict[tuple[uuid.UUID, uuid.UUID | None], dict] = {}
        for row in rows:
            key = (row.actor_id, row.materia_id)
            if key not in grouped:
                grouped[key] = {
                    "docente_id": str(row.actor_id),
                    "docente_nombre": nombre_completo_usuario(row.nombre, row.apellidos, row.email),
                    "materia_id": str(row.materia_id) if row.materia_id else "",
                    "materia_nombre": row.materia_nombre or "",
                    "total_acciones": 0,
                    "acciones_por_tipo": {},
                }
            grouped[key]["total_acciones"] += row.cnt
            grouped[key]["acciones_por_tipo"][row.accion] = (
                grouped[key]["acciones_por_tipo"].get(row.accion, 0) + row.cnt
            )
        return list(grouped.values())

    async def ultimas_acciones(
        self,
        session: AsyncSession,
        *,
        max_resultados: int = 200,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        accion: str | None = None,
        materias_ids: list[uuid.UUID] | None = None,
    ) -> Sequence[AuditLog]:
        query = (
            select(self._model)
            .where(self._model.tenant_id == self._tenant_id)
            .order_by(self._model.fecha_hora.desc())
        )
        if actor_id is not None:
            query = query.where(self._model.actor_id == actor_id)
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if accion is not None:
            query = query.where(self._model.accion == accion)
        if desde is not None:
            query = query.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            query = query.where(self._model.fecha_hora <= hasta)
        if materias_ids is not None:
            query = query.where(self._model.materia_id.in_(materias_ids))
        query = query.limit(max_resultados)
        result = await session.execute(query)
        return list(result.unique().scalars().all())
