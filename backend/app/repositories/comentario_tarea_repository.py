import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comentario_tarea import ComentarioTarea
from app.repositories.base import BaseRepository


class ComentarioTareaRepository(BaseRepository[ComentarioTarea]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(ComentarioTarea, tenant_id)

    async def list_por_tarea(
        self,
        session: AsyncSession,
        tarea_id: uuid.UUID,
        pagina: int = 1,
        page_size: int = 50,
    ) -> tuple[list[ComentarioTarea], int]:
        base = (
            select(ComentarioTarea)
            .where(
                ComentarioTarea.tenant_id == self._tenant_id,
                ComentarioTarea.deleted_at.is_(None),
                ComentarioTarea.tarea_id == tarea_id,
            )
            .order_by(ComentarioTarea.creado_at.asc())
        )

        count_q = base.with_only_columns(func.count())
        total_result = await session.execute(count_q)
        total = total_result.scalar_one()

        page_q = base.offset((pagina - 1) * page_size).limit(page_size)
        result = await session.execute(page_q)
        items = list(result.unique().scalars().all())

        return items, total
