import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.models.materia import Materia
from app.repositories.base import BaseRepository
from app.schemas.estructura import MateriaCreate, MateriaUpdate


class MateriaService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = BaseRepository[Materia](Materia, tenant_id)
        self._tenant_id = tenant_id

    async def create(self, db: AsyncSession, data: MateriaCreate) -> Materia:
        result = await db.execute(
            select(Materia).where(
                Materia.tenant_id == self._tenant_id,
                Materia.codigo == data.codigo,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise DomainError(f"Ya existe una materia con el código '{data.codigo}'")

        create_data = data.model_dump(exclude_unset=True)
        if create_data.get("carrera_id") is not None:
            create_data["carrera_id"] = uuid.UUID(create_data["carrera_id"])
        return await self._repo.create(db, create_data)

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Materia:
        entity = await self._repo.get(db, id)
        if entity is None:
            raise EntityNotFoundError(entity_type="Materia", entity_id=id)
        return entity

    async def get_all(
        self, db: AsyncSession, carrera_id: uuid.UUID | None = None
    ) -> list[Materia]:
        filters = {}
        if carrera_id is not None:
            filters["carrera_id"] = carrera_id
        return list(await self._repo.get_all(db, **filters))

    async def update(
        self, db: AsyncSession, id: uuid.UUID, data: MateriaUpdate
    ) -> Materia:
        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("carrera_id") is not None:
            update_data["carrera_id"] = uuid.UUID(update_data["carrera_id"])
        return await self._repo.update(db, id, update_data)

    async def soft_delete(self, db: AsyncSession, id: uuid.UUID) -> None:
        await self._repo.soft_delete(db, id)
