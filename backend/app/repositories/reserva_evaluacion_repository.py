import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.repositories.base import BaseRepository


class ReservaEvaluacionRepository(BaseRepository[ReservaEvaluacion]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(ReservaEvaluacion, tenant_id)

    async def get_activas_por_alumno(
        self, alumno_id: uuid.UUID, session: AsyncSession
    ) -> list[ReservaEvaluacion]:
        query = self._base_query().where(
            self._model.alumno_id == alumno_id,
            self._model.estado == EstadoReserva.ACTIVA,
        ).order_by(self._model.fecha_hora)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def get_activas_por_evaluacion(
        self, evaluacion_id: uuid.UUID, session: AsyncSession
    ) -> list[ReservaEvaluacion]:
        from app.models.evaluacion_dia import EvaluacionDia

        query = (
            select(ReservaEvaluacion)
            .join(EvaluacionDia, ReservaEvaluacion.evaluacion_dia_id == EvaluacionDia.id)
            .where(
                EvaluacionDia.evaluacion_id == evaluacion_id,
                ReservaEvaluacion.deleted_at.is_(None),
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
            )
            .order_by(ReservaEvaluacion.fecha_hora)
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def contar_activas(
        self, evaluacion_id: uuid.UUID, session: AsyncSession
    ) -> int:
        from app.models.evaluacion_dia import EvaluacionDia

        query = (
            select(func.count())
            .select_from(ReservaEvaluacion)
            .join(EvaluacionDia, ReservaEvaluacion.evaluacion_dia_id == EvaluacionDia.id)
            .where(
                EvaluacionDia.evaluacion_id == evaluacion_id,
                ReservaEvaluacion.deleted_at.is_(None),
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
            )
        )
        result = await session.execute(query)
        return result.scalar_one()
