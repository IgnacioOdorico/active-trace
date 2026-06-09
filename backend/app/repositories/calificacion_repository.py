import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.calificacion import Calificacion
from app.repositories.base import BaseRepository


class CalificacionRepository(BaseRepository[Calificacion]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Calificacion, tenant_id)

    async def bulk_upsert(
        self,
        session: AsyncSession,
        calificaciones: list[dict],
    ) -> dict[str, int]:
        insertadas = 0
        actualizadas = 0

        for data in calificaciones:
            data["tenant_id"] = self._tenant_id
            stmt = (
                pg_insert(Calificacion)
                .values(**data)
                .on_conflict_do_update(
                    constraint="uq_calificacion_entrada_actividad",
                    set_={
                        "nota_numerica": data.get("nota_numerica"),
                        "nota_textual": data.get("nota_textual"),
                        "aprobado": data.get("aprobado", False),
                        "origen": data.get("origen", "Importado"),
                        "importado_at": data.get("importado_at"),
                        "updated_at": datetime.now(timezone.utc),
                    },
                )
            )
            result = await session.execute(stmt)
            if result.rowcount == 1:
                insertadas += 1
            else:
                actualizadas += 1

        await session.flush()
        return {"insertadas": insertadas, "actualizadas": actualizadas}

    async def recalcular_aprobado_por_asignacion(
        self,
        session: AsyncSession,
        asignacion_id: uuid.UUID,
        umbral_pct: float,
        valores_aprobatorios: list[str] | None,
    ) -> int:
        subq = (
            update(Calificacion)
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
                Calificacion.materia_id.in_(
                    text(
                        "SELECT materia_id FROM asignaciones WHERE id = :asignacion_id"
                    ).bindparams(asignacion_id=asignacion_id)
                ),
            )
        )
        if valores_aprobatorios:
            subq = subq.values(
                aprobado=text(
                    """
                    CASE
                        WHEN nota_numerica IS NOT NULL AND nota_numerica >= :umbral THEN true
                        WHEN nota_textual IS NOT NULL AND nota_textual = ANY(:valores) THEN true
                        ELSE false
                    END
                    """
                ),
            )
        else:
            subq = subq.values(
                aprobado=text(
                    """
                    CASE
                        WHEN nota_numerica IS NOT NULL AND nota_numerica >= :umbral THEN true
                        ELSE false
                    END
                    """
                ),
            )

        result = await session.execute(
            subq,
            {
                "umbral": umbral_pct,
                "valores": valores_aprobatorios or [],
            },
        )
        await session.flush()
        return result.rowcount

    async def get_by_materia(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
    ) -> Sequence[Calificacion]:
        query = self._base_query().where(
            self._model.materia_id == materia_id,
        )
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def recalcular_aprobado_por_materia(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
        umbral_pct: float,
        valores_aprobatorios: list[str] | None,
    ) -> int:
        stmt = (
            update(Calificacion)
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
                Calificacion.materia_id == materia_id,
            )
        )
        if valores_aprobatorios:
            stmt = stmt.values(
                aprobado=text(
                    """
                    CASE
                        WHEN nota_numerica IS NOT NULL AND nota_numerica >= :umbral THEN true
                        WHEN nota_textual IS NOT NULL AND nota_textual = ANY(:valores) THEN true
                        ELSE false
                    END
                    """
                ),
            )
        else:
            stmt = stmt.values(
                aprobado=text(
                    """
                    CASE
                        WHEN nota_numerica IS NOT NULL AND nota_numerica >= :umbral THEN true
                        ELSE false
                    END
                    """
                ),
            )

        result = await session.execute(
            stmt,
            {"umbral": umbral_pct, "valores": valores_aprobatorios or []},
        )
        await session.flush()
        return result.rowcount
