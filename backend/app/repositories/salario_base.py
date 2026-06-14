import uuid
from datetime import date

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.models.salario_base import SalarioBase
from app.repositories.base import BaseRepository


class SalarioBaseRepository(BaseRepository[SalarioBase]):
    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(SalarioBase, tenant_id)

    async def _validar_solapamiento(
        self,
        session: AsyncSession,
        rol: str,
        desde: date,
        hasta: date | None,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        query = select(self._model).where(
            self._model.tenant_id == self._tenant_id,
            self._model.deleted_at.is_(None),
            self._model.rol == rol,
            self._model.desde < (hasta or date(9999, 12, 31)),
            or_(
                self._model.hasta.is_(None),
                self._model.hasta > desde,
            ),
        )
        if exclude_id is not None:
            query = query.where(self._model.id != exclude_id)
        result = await session.execute(query)
        existing = result.unique().scalar_one_or_none()
        if existing is not None:
            raise DomainError(
                detail=f"Ya existe un salario base para rol '{rol}' con vigencia solapada",
                context={"rol": rol, "desde": str(desde), "hasta": str(hasta)},
            )

    async def create(self, session: AsyncSession, data: dict) -> SalarioBase:
        await self._validar_solapamiento(
            session,
            rol=data["rol"],
            desde=data["desde"],
            hasta=data.get("hasta"),
        )
        return await super().create(session, data)

    async def update(
        self, session: AsyncSession, id: uuid.UUID, data: dict
    ) -> SalarioBase:
        entity = await self.get(session, id)
        if entity is None:
            from app.core.exceptions import EntityNotFoundError
            raise EntityNotFoundError(
                entity_type=self._model.__name__, entity_id=id
            )
        rol = data.get("rol", entity.rol)
        desde = data.get("desde", entity.desde)
        hasta = data.get("hasta", entity.hasta)
        await self._validar_solapamiento(
            session, rol=rol, desde=desde, hasta=hasta, exclude_id=id
        )
        return await super().update(session, id, data)
