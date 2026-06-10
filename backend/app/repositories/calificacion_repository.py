import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.calificacion import Calificacion
from app.models.entrada_padron import EntradaPadron
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

    async def get_by_materia_con_entrada(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
    ) -> Sequence[tuple[Calificacion, EntradaPadron]]:
        query = (
            select(Calificacion, EntradaPadron)
            .join(EntradaPadron, Calificacion.entrada_padron_id == EntradaPadron.id)
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
                Calificacion.materia_id == materia_id,
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        result = await session.execute(query)
        return list(result.unique().all())

    async def get_estado_por_materia(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
    ) -> Sequence[tuple[Calificacion, EntradaPadron]]:
        return await self.get_by_materia_con_entrada(session, materia_id)

    async def get_ranking_aprobadas(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
    ) -> Sequence[tuple[uuid.UUID, int]]:
        query = (
            select(
                Calificacion.entrada_padron_id,
                func.count().label("aprobadas"),
            )
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
                Calificacion.materia_id == materia_id,
                Calificacion.aprobado,
            )
            .group_by(Calificacion.entrada_padron_id)
            .having(func.count() >= 1)
            .order_by(func.count().desc())
        )
        result = await session.execute(query)
        return list(result.unique().all())

    async def get_notas_por_alumno(
        self,
        session: AsyncSession,
        materia_id: uuid.UUID,
        actividades: list[str],
    ) -> Sequence[tuple[Calificacion, EntradaPadron]]:
        query = (
            select(Calificacion, EntradaPadron)
            .join(EntradaPadron, Calificacion.entrada_padron_id == EntradaPadron.id)
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
                Calificacion.materia_id == materia_id,
                Calificacion.nombre_actividad.in_(actividades),
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        result = await session.execute(query)
        return list(result.unique().all())

    async def get_filtrado(
        self,
        session: AsyncSession,
        *,
        materia_id: uuid.UUID | None = None,
        regional: str | None = None,
        comision: str | None = None,
        q: str | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        entrada_padron_id: uuid.UUID | None = None,
        pagina: int = 1,
        por_pagina: int = 50,
    ) -> tuple[Sequence[tuple[Calificacion, EntradaPadron]], int]:
        query = (
            select(Calificacion, EntradaPadron)
            .join(EntradaPadron, Calificacion.entrada_padron_id == EntradaPadron.id)
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )

        if materia_id is not None:
            query = query.where(Calificacion.materia_id == materia_id)
        if regional is not None:
            query = query.where(EntradaPadron.regional == regional)
        if comision is not None:
            query = query.where(EntradaPadron.comision == comision)
        if q is not None:
            query = query.where(
                EntradaPadron.nombre.ilike(f"%{q}%")
                | EntradaPadron.apellidos.ilike(f"%{q}%")
            )
        if desde is not None:
            query = query.where(Calificacion.importado_at >= desde)
        if hasta is not None:
            query = query.where(Calificacion.importado_at <= hasta)
        if entrada_padron_id is not None:
            query = query.where(Calificacion.entrada_padron_id == entrada_padron_id)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()

        offset = (pagina - 1) * por_pagina
        query = query.offset(offset).limit(por_pagina)

        result = await session.execute(query)
        items = list(result.unique().all())

        return items, total
