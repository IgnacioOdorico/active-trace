import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.asignacion import Asignacion
from app.repositories.asignacion import AsignacionRepository
from app.schemas.asignaciones import AsignacionCreate, AsignacionUpdate


class AsignacionService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = AsignacionRepository(tenant_id)

    @staticmethod
    def _uuid_fields(data: dict) -> dict:
        uuid_keys = {
            "usuario_id",
            "materia_id",
            "carrera_id",
            "cohorte_id",
            "responsable_id",
        }
        for key in uuid_keys:
            value = data.get(key)
            if value is not None:
                data[key] = uuid.UUID(value)
        return data

    async def create(self, db: AsyncSession, data: AsignacionCreate) -> Asignacion:
        create_data = self._uuid_fields(data.model_dump(exclude_unset=True))
        return await self._repo.create(db, create_data)

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Asignacion:
        entity = await self._repo.get(db, id)
        if entity is None:
            raise EntityNotFoundError(entity_type="Asignacion", entity_id=id)
        return entity

    async def get_all(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        usuario_id: str | None = None,
        materia_id: str | None = None,
        carrera_id: str | None = None,
        cohorte_id: str | None = None,
        rol: str | None = None,
    ) -> tuple[list[Asignacion], int]:
        filters = {}
        if usuario_id is not None:
            filters["usuario_id"] = uuid.UUID(usuario_id)
        if materia_id is not None:
            filters["materia_id"] = uuid.UUID(materia_id)
        if carrera_id is not None:
            filters["carrera_id"] = uuid.UUID(carrera_id)
        if cohorte_id is not None:
            filters["cohorte_id"] = uuid.UUID(cohorte_id)
        if rol is not None:
            filters["rol"] = rol

        total = await self._repo.count(db, **filters)
        asignaciones = list(await self._repo.get_all(db, **filters))

        start = (page - 1) * page_size
        end = start + page_size
        return asignaciones[start:end], total

    async def update(
        self, db: AsyncSession, id: uuid.UUID, data: AsignacionUpdate
    ) -> Asignacion:
        entity = await self._repo.get(db, id)
        if entity is None:
            raise EntityNotFoundError(entity_type="Asignacion", entity_id=id)

        update_data = self._uuid_fields(data.model_dump(exclude_unset=True))
        return await self._repo.update(db, id, update_data)

    async def soft_delete(self, db: AsyncSession, id: uuid.UUID) -> None:
        await self._repo.soft_delete(db, id)
