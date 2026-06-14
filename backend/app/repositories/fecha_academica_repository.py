import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fecha_academica import FechaAcademica
from app.repositories.base import BaseRepository


class FechaAcademicaRepository(BaseRepository[FechaAcademica]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(FechaAcademica, tenant_id)

    async def get_by_materia_cohorte(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> list[FechaAcademica]:
        query = (
            self._base_query()
            .where(
                self._model.materia_id == materia_id,
                self._model.cohorte_id == cohorte_id,
            )
            .order_by(self._model.fecha.asc())
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())
