import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instancia_encuentro import InstanciaEncuentro
from app.repositories.base import BaseRepository


class InstanciaEncuentroRepository(BaseRepository[InstanciaEncuentro]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(InstanciaEncuentro, tenant_id)

    async def get_by_slot(
        self, session: AsyncSession, slot_id: uuid.UUID
    ) -> list[InstanciaEncuentro]:
        query = self._base_query().where(self._model.slot_id == slot_id)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def get_by_materia_filtros(
        self,
        session: AsyncSession,
        *,
        materia_id: uuid.UUID | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        estado: str | None = None,
    ) -> list[InstanciaEncuentro]:
        query = self._base_query()
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if fecha_desde is not None:
            query = query.where(self._model.fecha >= fecha_desde)
        if fecha_hasta is not None:
            query = query.where(self._model.fecha <= fecha_hasta)
        if estado is not None:
            query = query.where(self._model.estado == estado)
        query = query.order_by(self._model.fecha.desc())
        result = await session.execute(query)
        return list(result.unique().scalars().all())
