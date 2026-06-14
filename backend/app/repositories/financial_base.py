import uuid
from collections.abc import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.financial_base import FinancialEntityMeta


class FinancialRepository[T: FinancialEntityMeta]:
    def __init__(self, model: type[T], tenant_id: uuid.UUID) -> None:
        self._model = model
        self._tenant_id = tenant_id

    def _base_query(self):
        return select(self._model).where(
            self._model.tenant_id == self._tenant_id,
        )

    async def create(self, session: AsyncSession, data: dict) -> T:
        instance = self._model(tenant_id=self._tenant_id, **data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def get(self, session: AsyncSession, id: uuid.UUID) -> T | None:
        query = self._base_query().where(self._model.id == id)
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        **filters,
    ) -> Sequence[T]:
        query = self._base_query()
        for attr, value in filters.items():
            query = query.where(getattr(self._model, attr) == value)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def update(
        self, session: AsyncSession, id: uuid.UUID, data: dict
    ) -> T:
        entity = await self.get(session, id)
        if entity is None:
            raise EntityNotFoundError(
                entity_type=self._model.__name__, entity_id=id
            )
        for key, value in data.items():
            setattr(entity, key, value)
        await session.flush()
        await session.refresh(entity)
        return entity

    async def count(
        self, session: AsyncSession, **filters
    ) -> int:
        query = select(func.count()).select_from(self._model).where(
            self._model.tenant_id == self._tenant_id,
        )
        for attr, value in filters.items():
            query = query.where(getattr(self._model, attr) == value)
        result = await session.execute(query)
        return result.scalar_one()
