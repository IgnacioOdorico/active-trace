import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.models.cohorte import Cohorte
from app.repositories.base import BaseRepository
from app.schemas.estructura import CohorteCreate, CohorteUpdate
from app.services.carrera_service import CarreraService


class CohorteService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = BaseRepository[Cohorte](Cohorte, tenant_id)
        self._tenant_id = tenant_id
        self._carrera_svc = CarreraService(tenant_id)

    async def create(self, db: AsyncSession, data: CohorteCreate) -> Cohorte:
        await self._carrera_svc.validate_activa(db, uuid.UUID(data.carrera_id))

        result = await db.execute(
            select(Cohorte).where(
                Cohorte.tenant_id == self._tenant_id,
                Cohorte.carrera_id == uuid.UUID(data.carrera_id),
                Cohorte.nombre == data.nombre,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise DomainError(
                f"Ya existe un cohorte con el nombre '{data.nombre}' "
                f"en esta carrera"
            )

        create_data = data.model_dump(exclude_unset=True)
        create_data["carrera_id"] = uuid.UUID(data.carrera_id)
        return await self._repo.create(db, create_data)

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Cohorte:
        entity = await self._repo.get(db, id)
        if entity is None:
            raise EntityNotFoundError(entity_type="Cohorte", entity_id=id)
        return entity

    async def get_all(
        self, db: AsyncSession, carrera_id: uuid.UUID | None = None
    ) -> list[Cohorte]:
        filters = {}
        if carrera_id is not None:
            filters["carrera_id"] = carrera_id
        return list(await self._repo.get_all(db, **filters))

    async def update(
        self, db: AsyncSession, id: uuid.UUID, data: CohorteUpdate
    ) -> Cohorte:
        update_data = data.model_dump(exclude_unset=True)
        return await self._repo.update(db, id, update_data)

    async def soft_delete(self, db: AsyncSession, id: uuid.UUID) -> None:
        await self._repo.soft_delete(db, id)
