import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.models.factura import Factura
from app.repositories.financial_base import FinancialRepository


class FacturaRepository(FinancialRepository[Factura]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Factura, tenant_id)

    async def listar_por_filtros(
        self,
        session: AsyncSession,
        periodo: str | None = None,
        estado: str | None = None,
    ) -> list[Factura]:
        query = self._base_query()
        if periodo is not None:
            query = query.where(self._model.periodo == periodo)
        if estado is not None:
            query = query.where(self._model.estado == estado)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def abonar(
        self, session: AsyncSession, id: uuid.UUID
    ) -> Factura:
        entity = await self.get(session, id)
        if entity is None:
            raise EntityNotFoundError(
                entity_type="Factura", entity_id=id
            )
        if entity.estado == "Abonada":
            raise DomainError(
                detail="La factura ya está abonada",
                context={"factura_id": str(id)},
            )
        entity.estado = "Abonada"
        entity.abonada_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(entity)
        return entity
