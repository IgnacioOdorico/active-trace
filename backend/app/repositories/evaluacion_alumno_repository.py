import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluacion_alumno import EvaluacionAlumno
from app.repositories.base import BaseRepository


class EvaluacionAlumnoRepository(BaseRepository[EvaluacionAlumno]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(EvaluacionAlumno, tenant_id)

    async def reemplazar_padron(
        self,
        evaluacion_id: uuid.UUID,
        alumno_ids: list[uuid.UUID],
        session: AsyncSession,
    ) -> int:
        delete_query = (
            select(EvaluacionAlumno)
            .where(
                EvaluacionAlumno.evaluacion_id == evaluacion_id,
                EvaluacionAlumno.deleted_at.is_(None),
            )
        )
        existing = await session.execute(delete_query)
        for ea in existing.unique().scalars().all():
            await session.delete(ea)

        for alumno_id in alumno_ids:
            session.add(
                EvaluacionAlumno(
                    tenant_id=self._tenant_id,
                    evaluacion_id=evaluacion_id,
                    alumno_id=alumno_id,
                )
            )

        await session.flush()
        return len(alumno_ids)

    async def get_alumnos_habilitados(
        self, evaluacion_id: uuid.UUID, session: AsyncSession
    ) -> list[EvaluacionAlumno]:
        query = select(EvaluacionAlumno).where(
            EvaluacionAlumno.evaluacion_id == evaluacion_id,
            EvaluacionAlumno.deleted_at.is_(None),
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def get_alumnos_habilitados_por_alumno(
        self, alumno_id: uuid.UUID, session: AsyncSession
    ) -> list[EvaluacionAlumno]:
        query = select(EvaluacionAlumno).where(
            EvaluacionAlumno.alumno_id == alumno_id,
            EvaluacionAlumno.deleted_at.is_(None),
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())
