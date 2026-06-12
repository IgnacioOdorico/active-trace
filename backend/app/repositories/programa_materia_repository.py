import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.programa_materia import ProgramaMateria
from app.repositories.base import BaseRepository


class ProgramaMateriaRepository(BaseRepository[ProgramaMateria]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(ProgramaMateria, tenant_id)

    async def get_by_materia_carrera_cohorte(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> list[ProgramaMateria]:
        query = self._base_query().where(
            self._model.materia_id == materia_id,
            self._model.carrera_id == carrera_id,
            self._model.cohorte_id == cohorte_id,
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())
