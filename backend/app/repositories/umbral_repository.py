import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.umbral_materia import UmbralMateria
from app.repositories.base import BaseRepository


class UmbralRepository(BaseRepository[UmbralMateria]):
    UMBRAL_DEFECTO = 60.0

    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(UmbralMateria, tenant_id)

    async def get_by_asignacion(
        self,
        session: AsyncSession,
        asignacion_id: uuid.UUID,
    ) -> UmbralMateria | None:
        query = self._base_query().where(
            self._model.asignacion_id == asignacion_id,
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()

    async def upsert(
        self,
        session: AsyncSession,
        asignacion_id: uuid.UUID,
        materia_id: uuid.UUID,
        umbral_pct: float,
        valores_aprobatorios: list[str] | None = None,
    ) -> UmbralMateria:
        stmt = (
            pg_insert(UmbralMateria)
            .values(
                tenant_id=self._tenant_id,
                asignacion_id=asignacion_id,
                materia_id=materia_id,
                umbral_pct=umbral_pct,
                valores_aprobatorios=valores_aprobatorios,
            )
            .on_conflict_do_update(
                constraint="umbral_materia_asignacion_id_key",
                set_={
                    "umbral_pct": umbral_pct,
                    "valores_aprobatorios": valores_aprobatorios,
                    "materia_id": materia_id,
                },
            )
        )
        result = await session.execute(stmt)
        await session.flush()

        existing = await self.get_by_asignacion(session, asignacion_id)
        if existing is not None:
            await session.refresh(existing)
            return existing

        return result.scalar_one()

    def get_umbral_efectivo(
        self,
        umbral: UmbralMateria | None,
    ) -> tuple[float, list[str] | None]:
        if umbral is None:
            return self.UMBRAL_DEFECTO, None
        return umbral.umbral_pct, umbral.valores_aprobatorios
