import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.repositories.base import BaseRepository


class ResultadoEvaluacionRepository(BaseRepository[ResultadoEvaluacion]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(ResultadoEvaluacion, tenant_id)

    async def get_por_evaluacion(
        self, evaluacion_id: uuid.UUID, session: AsyncSession
    ) -> list[ResultadoEvaluacion]:
        query = (
            select(ResultadoEvaluacion)
            .where(
                ResultadoEvaluacion.evaluacion_id == evaluacion_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
            .order_by(ResultadoEvaluacion.created_at)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def upsert(
        self,
        evaluacion_id: uuid.UUID,
        alumno_id: uuid.UUID,
        nota_final: str,
        session: AsyncSession,
    ) -> ResultadoEvaluacion:
        query = (
            select(ResultadoEvaluacion)
            .where(
                ResultadoEvaluacion.evaluacion_id == evaluacion_id,
                ResultadoEvaluacion.alumno_id == alumno_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        result = await session.execute(query)
        existing = result.unique().scalar_one_or_none()

        if existing:
            existing.nota_final = nota_final
            await session.flush()
            await session.refresh(existing)
            return existing

        return await self.create(
            session,
            {
                "evaluacion_id": evaluacion_id,
                "alumno_id": alumno_id,
                "nota_final": nota_final,
            },
        )
