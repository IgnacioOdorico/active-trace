import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.models.liquidacion import Liquidacion
from app.repositories.financial_base import FinancialRepository


class LiquidacionRepository(FinancialRepository[Liquidacion]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(Liquidacion, tenant_id)

    def _base_query(self):
        return super()._base_query().where(self._model.deleted_at.is_(None))

    async def soft_delete_abiertas(
        self,
        session: AsyncSession,
        cohorte_id: uuid.UUID,
        periodo: str,
    ) -> None:
        """Soft-delete del borrador: descarta las liquidaciones 'Abierta'
        previas de esta cohorte+período antes de recalcular. Nunca toca
        'Cerrada' (esas ya bloquean el recálculo con 409 antes de llegar aquí)."""
        await session.execute(
            update(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.cohorte_id == cohorte_id,
                self._model.periodo == periodo,
                self._model.estado == "Abierta",
                self._model.deleted_at.is_(None),
            )
            .values(deleted_at=datetime.now(timezone.utc))
        )

    async def listar_por_periodo(
        self,
        session: AsyncSession,
        periodo: str,
        cohorte_id: uuid.UUID | None = None,
    ) -> list[Liquidacion]:
        query = self._base_query().where(
            self._model.periodo == periodo,
        )
        if cohorte_id is not None:
            query = query.where(self._model.cohorte_id == cohorte_id)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def listar_todas(
        self,
        session: AsyncSession,
        cohorte_id: uuid.UUID | None = None,
    ) -> list[Liquidacion]:
        query = self._base_query()
        if cohorte_id is not None:
            query = query.where(self._model.cohorte_id == cohorte_id)
        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def periodo_cerrado(
        self,
        session: AsyncSession,
        cohorte_id: uuid.UUID,
        periodo: str,
    ) -> bool:
        query = select(func.count()).select_from(self._model).where(
            self._model.tenant_id == self._tenant_id,
            self._model.cohorte_id == cohorte_id,
            self._model.periodo == periodo,
            self._model.estado == "Cerrada",
            self._model.deleted_at.is_(None),
        )
        result = await session.execute(query)
        return result.scalar_one() > 0

    async def cerrar(
        self, session: AsyncSession, id: uuid.UUID
    ) -> Liquidacion:
        entity = await self.get(session, id)
        if entity is None:
            raise EntityNotFoundError(
                entity_type="Liquidacion", entity_id=id
            )
        if entity.estado == "Cerrada":
            raise DomainError(
                detail="La liquidación ya está cerrada",
                context={"liquidacion_id": str(id)},
            )
        entity.estado = "Cerrada"
        await session.flush()
        await session.refresh(entity)
        return entity

    async def _validar_no_cerrada(self, session: AsyncSession, id: uuid.UUID) -> Liquidacion:
        entity = await self.get(session, id)
        if entity is None:
            raise EntityNotFoundError(
                entity_type="Liquidacion", entity_id=id
            )
        if entity.estado == "Cerrada":
            raise DomainError(
                detail="No se puede modificar una liquidación cerrada",
                context={"liquidacion_id": str(id)},
            )
        return entity

    async def obtener_kpis(
        self,
        session: AsyncSession,
        periodo: str,
    ) -> dict:
        query_general = self._base_query().where(
            self._model.periodo == periodo,
            self._model.es_nexo == False,
        )
        result = await session.execute(query_general)
        generales = list(result.unique().scalars().all())

        query_nexo = self._base_query().where(
            self._model.periodo == periodo,
            self._model.es_nexo == True,
        )
        result = await session.execute(query_nexo)
        nexo_items = list(result.unique().scalars().all())

        total_general = sum(float(l.total) for l in generales if not l.excluido_por_factura)
        total_nexo = sum(float(l.total) for l in nexo_items)
        cant_general = len([l for l in generales if not l.excluido_por_factura])
        cant_nexo = len(nexo_items)
        cant_facturantes = len([l for l in generales if l.excluido_por_factura])

        return {
            "total_general": total_general,
            "total_nexo": total_nexo,
            "total_facturas_pendientes": 0.0,
            "total_facturas_abonadas": 0.0,
            "cantidad_docentes_general": cant_general,
            "cantidad_docentes_nexo": cant_nexo,
            "cantidad_docentes_facturantes": cant_facturantes,
        }
