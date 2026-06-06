import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.models.carrera import Carrera
from app.repositories.base import BaseRepository
from app.schemas.estructura import CarreraCreate, CarreraUpdate


class CarreraService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = BaseRepository[Carrera](Carrera, tenant_id)
        self._tenant_id = tenant_id

    async def create(self, db: AsyncSession, data: CarreraCreate) -> Carrera:
        result = await db.execute(
            select(Carrera).where(
                Carrera.tenant_id == self._tenant_id,
                Carrera.codigo == data.codigo,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise DomainError(f"Ya existe una carrera con el código '{data.codigo}'")

        return await self._repo.create(
            db, data.model_dump(exclude_unset=True)
        )

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Carrera:
        entity = await self._repo.get(db, id)
        if entity is None:
            raise EntityNotFoundError(entity_type="Carrera", entity_id=id)
        return entity

    async def get_all(self, db: AsyncSession) -> list[Carrera]:
        return list(await self._repo.get_all(db))

    async def update(
        self, db: AsyncSession, id: uuid.UUID, data: CarreraUpdate
    ) -> Carrera:
        return await self._repo.update(
            db, id, data.model_dump(exclude_unset=True)
        )

    async def soft_delete(self, db: AsyncSession, id: uuid.UUID) -> None:
        await self._repo.soft_delete(db, id)

    async def validate_activa(self, db: AsyncSession, id: uuid.UUID) -> Carrera:
        entity = await self.get(db, id)
        if not entity.activa:
            raise DomainError("La carrera no está activa")
        return entity
