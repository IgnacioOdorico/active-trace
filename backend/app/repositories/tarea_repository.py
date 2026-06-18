import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarea import Tarea
from app.repositories.base import BaseRepository


class TareaRepository(BaseRepository[Tarea]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Tarea, tenant_id)

    async def list_mias(
        self,
        session: AsyncSession,
        usuario_id: uuid.UUID,
        estado: str | None = None,
        pagina: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Tarea], int]:
        base = (
            select(Tarea)
            .where(
                Tarea.tenant_id == self._tenant_id,
                Tarea.deleted_at.is_(None),
                Tarea.asignado_a == usuario_id,
            )
            .order_by(Tarea.created_at.desc())
        )

        if estado:
            base = base.where(Tarea.estado == estado)

        count_q = base.order_by(None).with_only_columns(func.count())
        total_result = await session.execute(count_q)
        total = total_result.scalar_one()

        page_q = base.offset((pagina - 1) * page_size).limit(page_size)
        result = await session.execute(page_q)
        items = list(result.unique().scalars().all())

        return items, total

    async def list_todas(
        self,
        session: AsyncSession,
        asignado_a: uuid.UUID | None = None,
        asignado_por: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
        busqueda: str | None = None,
        pagina: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Tarea], int]:
        base = (
            select(Tarea)
            .where(
                Tarea.tenant_id == self._tenant_id,
                Tarea.deleted_at.is_(None),
            )
            .order_by(Tarea.created_at.desc())
        )

        if asignado_a is not None:
            base = base.where(Tarea.asignado_a == asignado_a)
        if asignado_por is not None:
            base = base.where(Tarea.asignado_por == asignado_por)
        if materia_id is not None:
            base = base.where(Tarea.materia_id == materia_id)
        if estado is not None:
            base = base.where(Tarea.estado == estado)
        if busqueda:
            base = base.where(Tarea.descripcion.ilike(f"%{busqueda}%"))

        count_q = base.order_by(None).with_only_columns(func.count())
        total_result = await session.execute(count_q)
        total = total_result.scalar_one()

        page_q = base.offset((pagina - 1) * page_size).limit(page_size)
        result = await session.execute(page_q)
        items = list(result.unique().scalars().all())

        return items, total
