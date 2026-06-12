import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import AlcanceAviso, Aviso
from app.repositories.base import BaseRepository


class AvisoRepository(BaseRepository[Aviso]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Aviso, tenant_id)

    async def list_visibles(
        self,
        session: AsyncSession,
        usuario_id: uuid.UUID,
        roles: list[str],
        materia_ids: list[uuid.UUID],
        cohorte_ids: list[uuid.UUID],
        pagina: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Aviso], int]:
        now = datetime.now(timezone.utc)
        base = (
            select(Aviso)
            .where(
                Aviso.tenant_id == self._tenant_id,
                Aviso.deleted_at.is_(None),
                Aviso.activo,
                Aviso.inicio_en <= now,
                Aviso.fin_en >= now,
            )
        )

        clauses = []

        clauses.append(Aviso.alcance == AlcanceAviso.GLOBAL)

        if materia_ids:
            clauses.append(
                and_(
                    Aviso.alcance == AlcanceAviso.POR_MATERIA,
                    Aviso.materia_id.in_(materia_ids),
                )
            )

        if cohorte_ids:
            clauses.append(
                and_(
                    Aviso.alcance == AlcanceAviso.POR_COHORTE,
                    Aviso.cohorte_id.in_(cohorte_ids),
                )
            )

        if roles:
            clauses.append(
                and_(
                    Aviso.alcance == AlcanceAviso.POR_ROL,
                    Aviso.rol_destino.in_(roles),
                )
            )

        if clauses:
            base = base.where(or_(*clauses))

        base = base.order_by(Aviso.orden.asc())

        count_q = base.with_only_columns(func.count())
        total_result = await session.execute(count_q)
        total = total_result.scalar_one()

        page_q = base.offset((pagina - 1) * page_size).limit(page_size)
        result = await session.execute(page_q)
        items = list(result.unique().scalars().all())

        return items, total

    async def list_gestion(
        self,
        session: AsyncSession,
        pagina: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Aviso], int]:
        base = (
            select(Aviso)
            .where(
                Aviso.tenant_id == self._tenant_id,
                Aviso.deleted_at.is_(None),
            )
            .order_by(Aviso.created_at.desc())
        )

        count_q = base.with_only_columns(func.count())
        total_result = await session.execute(count_q)
        total = total_result.scalar_one()

        page_q = base.offset((pagina - 1) * page_size).limit(page_size)
        result = await session.execute(page_q)
        items = list(result.unique().scalars().all())

        return items, total

    async def get_with_deleted(
        self, session: AsyncSession, id: uuid.UUID
    ) -> Aviso | None:
        query = select(Aviso).where(
            Aviso.tenant_id == self._tenant_id,
            Aviso.id == id,
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()
