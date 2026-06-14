import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.schemas.programa import (
    ProgramaMateriaCreateRequest,
    ProgramaMateriaUpdateRequest,
)


class ProgramaService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = ProgramaMateriaRepository(tenant_id)
        self._tenant_id = tenant_id

    async def crear(
        self, db: AsyncSession, data: ProgramaMateriaCreateRequest
    ) -> dict:
        create_data = data.model_dump()
        for fk in ("materia_id", "carrera_id", "cohorte_id"):
            create_data[fk] = uuid.UUID(create_data[fk])
        create_data["cargado_at"] = datetime.now(timezone.utc)
        entity = await self._repo.create(db, create_data)
        return {"id": str(entity.id)}

    async def obtener(self, db: AsyncSession, id: uuid.UUID) -> dict:
        entity = await self._repo.get(db, id)
        if entity is None:
            raise EntityNotFoundError(entity_type="ProgramaMateria", entity_id=id)
        return {
            "id": str(entity.id),
            "tenant_id": str(entity.tenant_id),
            "materia_id": str(entity.materia_id),
            "carrera_id": str(entity.carrera_id),
            "cohorte_id": str(entity.cohorte_id),
            "titulo": entity.titulo,
            "referencia_archivo": entity.referencia_archivo,
            "cargado_at": entity.cargado_at.isoformat(),
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
        }

    async def listar(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
    ) -> dict:
        filters = {}
        if materia_id is not None:
            filters["materia_id"] = materia_id
        if carrera_id is not None:
            filters["carrera_id"] = carrera_id
        if cohorte_id is not None:
            filters["cohorte_id"] = cohorte_id
        items = await self._repo.get_all(db, **filters)
        return {
            "items": [
                {
                    "id": str(e.id),
                    "materia_id": str(e.materia_id),
                    "carrera_id": str(e.carrera_id),
                    "cohorte_id": str(e.cohorte_id),
                    "titulo": e.titulo,
                    "referencia_archivo": e.referencia_archivo,
                    "cargado_at": e.cargado_at.isoformat(),
                    "created_at": e.created_at.isoformat(),
                    "updated_at": e.updated_at.isoformat(),
                }
                for e in items
            ],
            "total": len(items),
        }

    async def editar(
        self, db: AsyncSession, id: uuid.UUID, data: ProgramaMateriaUpdateRequest
    ) -> dict:
        update_data = data.model_dump(exclude_unset=True)
        entity = await self._repo.update(db, id, update_data)
        return {"id": str(entity.id)}

    async def eliminar(self, db: AsyncSession, id: uuid.UUID) -> None:
        await self._repo.soft_delete(db, id)
