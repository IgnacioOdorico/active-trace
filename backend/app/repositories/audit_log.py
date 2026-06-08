import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


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
