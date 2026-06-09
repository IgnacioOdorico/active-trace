import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.umbral_repository import UmbralRepository
from app.repositories.calificacion_repository import CalificacionRepository


class UmbralService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._umbral_repo = UmbralRepository(tenant_id)
        self._calificacion_repo = CalificacionRepository(tenant_id)

    async def configurar(
        self,
        db: AsyncSession,
        asignacion_id: uuid.UUID,
        materia_id: uuid.UUID,
        umbral_pct: float,
        valores_aprobatorios: list[str] | None = None,
    ) -> dict[str, Any]:
        umbral = await self._umbral_repo.upsert(
            db,
            asignacion_id=asignacion_id,
            materia_id=materia_id,
            umbral_pct=umbral_pct,
            valores_aprobatorios=valores_aprobatorios,
        )

        recalculo = await self._calificacion_repo.recalcular_aprobado_por_materia(
            db,
            materia_id=materia_id,
            umbral_pct=umbral_pct,
            valores_aprobatorios=valores_aprobatorios,
        )

        return {
            "id": str(umbral.id),
            "asignacion_id": str(umbral.asignacion_id),
            "materia_id": str(umbral.materia_id),
            "umbral_pct": umbral.umbral_pct,
            "valores_aprobatorios": umbral.valores_aprobatorios,
            "recalculo_aprobados": recalculo,
        }

    async def obtener_vigente(
        self,
        db: AsyncSession,
        asignacion_id: uuid.UUID,
    ) -> dict[str, Any]:
        umbral = await self._umbral_repo.get_by_asignacion(db, asignacion_id)
        pct, valores = self._umbral_repo.get_umbral_efectivo(umbral)

        return {
            "asignacion_id": str(asignacion_id),
            "umbral_pct": pct,
            "valores_aprobatorios": valores,
            "es_configurado": umbral is not None,
        }
