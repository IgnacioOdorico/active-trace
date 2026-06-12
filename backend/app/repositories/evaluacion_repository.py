import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluacion import Evaluacion
from app.repositories.base import BaseRepository


class EvaluacionRepository(BaseRepository[Evaluacion]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Evaluacion, tenant_id)

    async def get_with_metricas(
        self, evaluacion_id: uuid.UUID, session: AsyncSession
    ) -> Evaluacion | None:
        return await self.get(session, evaluacion_id)

    async def list_all_con_metricas(
        self,
        session: AsyncSession,
        *,
        materia_id: uuid.UUID | None = None,
        pagina: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Evaluacion], int]:
        query = self._base_query()
        if materia_id is not None:
            query = query.where(self._model.materia_id == materia_id)
        query = query.order_by(self._model.created_at.desc())

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_query)
        total = total_result.scalar_one()

        offset = (pagina - 1) * page_size
        paginated = query.offset(offset).limit(page_size)
        result = await session.execute(paginated)
        items = list(result.unique().scalars().all())

        return items, total
