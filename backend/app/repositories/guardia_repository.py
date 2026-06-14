import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardia import Guardia
from app.repositories.base import BaseRepository


class GuardiaRepository(BaseRepository[Guardia]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Guardia, tenant_id)

    async def get_by_asignacion(
        self, session: AsyncSession, asignacion_id: uuid.UUID
    ) -> list[Guardia]:
        query = self._base_query().where(self._model.asignacion_id == asignacion_id)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def get_all_filtros(
        self,
        session: AsyncSession,
        *,
        materia_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
    ) -> list[Guardia]:
        query = self._base_query()
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        if asignacion_id is not None:
            query = query.where(self._model.asignacion_id == asignacion_id)
        query = query.order_by(self._model.created_at.desc())
        result = await session.execute(query)
        return list(result.unique().scalars().all())
