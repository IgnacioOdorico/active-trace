import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comunicacion import Comunicacion
from app.repositories.base import BaseRepository


class ComunicacionRepository(BaseRepository[Comunicacion]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Comunicacion, tenant_id)

    async def get_pendientes(
        self, session: AsyncSession, limit: int = 50
    ) -> list[Comunicacion]:
        query = (
            self._base_query()
            .where(self._model.estado == "Pendiente")
            .order_by(self._model.created_at)
            .limit(limit)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    @staticmethod
    async def get_all_pendientes_cross_tenant(
        session: AsyncSession, limit: int = 50
    ) -> list[Comunicacion]:
        query = (
            select(Comunicacion)
            .where(
                Comunicacion.estado == "Pendiente",
                Comunicacion.deleted_at.is_(None),
            )
            .order_by(Comunicacion.created_at)
            .limit(limit)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def get_by_lote(
        self, session: AsyncSession, lote_id: uuid.UUID
    ) -> list[Comunicacion]:
        query = self._base_query().where(self._model.lote_id == lote_id)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def batch_update_estado(
        self,
        session: AsyncSession,
        lote_id: uuid.UUID,
        estado_origen: str,
        estado_destino: str,
    ) -> int:
        stmt = (
            update(Comunicacion)
            .where(
                Comunicacion.tenant_id == self._tenant_id,
                Comunicacion.deleted_at.is_(None),
                Comunicacion.lote_id == lote_id,
                Comunicacion.estado == estado_origen,
            )
            .values(estado=estado_destino)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount

    async def count_by_lote(
        self, session: AsyncSession, lote_id: uuid.UUID
    ) -> int:
        query = (
            select(func.count())
            .select_from(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.deleted_at.is_(None),
                self._model.lote_id == lote_id,
            )
        )
        result = await session.execute(query)
        return result.scalar_one()
