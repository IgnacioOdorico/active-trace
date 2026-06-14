import uuid

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluacion_dia import EvaluacionDia
from app.repositories.base import BaseRepository


class EvaluacionDiaRepository(BaseRepository[EvaluacionDia]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(EvaluacionDia, tenant_id)

    async def decrementar_cupo(
        self, dia_id: uuid.UUID, session: AsyncSession
    ) -> bool:
        stmt = (
            update(EvaluacionDia)
            .where(EvaluacionDia.id == dia_id, EvaluacionDia.cupos_restantes > 0)
            .values(cupos_restantes=EvaluacionDia.cupos_restantes - 1)
        )
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def incrementar_cupo(
        self, dia_id: uuid.UUID, session: AsyncSession
    ) -> bool:
        stmt = (
            update(EvaluacionDia)
            .where(EvaluacionDia.id == dia_id)
            .values(cupos_restantes=EvaluacionDia.cupos_restantes + 1)
        )
        result = await session.execute(stmt)
        return result.rowcount > 0

    async def get_by_evaluacion(
        self, evaluacion_id: uuid.UUID, session: AsyncSession
    ) -> list[EvaluacionDia]:
        query = self._base_query().where(
            self._model.evaluacion_id == evaluacion_id
        ).order_by(self._model.fecha)
        result = await session.execute(query)
        return list(result.unique().scalars().all())
