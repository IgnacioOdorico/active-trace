import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.schemas.fecha_academica import (
    FechaAcademicaCreateRequest,
    FechaAcademicaUpdateRequest,
)


class FechaAcademicaService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._repo = FechaAcademicaRepository(tenant_id)
        self._tenant_id = tenant_id

    async def crear(
        self, db: AsyncSession, data: FechaAcademicaCreateRequest
    ) -> dict:
        create_data = data.model_dump()
        for fk in ("materia_id", "cohorte_id"):
            create_data[fk] = uuid.UUID(create_data[fk])
        entity = await self._repo.create(db, create_data)
        return {"id": str(entity.id)}

    async def obtener(self, db: AsyncSession, id: uuid.UUID) -> dict:
        entity = await self._repo.get(db, id)
        if entity is None:
            raise EntityNotFoundError(
                entity_type="FechaAcademica", entity_id=id
            )
        return {
            "id": str(entity.id),
            "tenant_id": str(entity.tenant_id),
            "materia_id": str(entity.materia_id),
            "cohorte_id": str(entity.cohorte_id),
            "tipo": entity.tipo,
            "numero": entity.numero,
            "periodo": entity.periodo,
            "fecha": entity.fecha.isoformat(),
            "titulo": entity.titulo,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
        }

    async def listar(
        self,
        db: AsyncSession,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
    ) -> dict:
        filters = {}
        if materia_id is not None:
            filters["materia_id"] = materia_id
        if cohorte_id is not None:
            filters["cohorte_id"] = cohorte_id
        items = await self._repo.get_all(db, **filters)
        return {
            "items": [
                {
                    "id": str(e.id),
                    "materia_id": str(e.materia_id),
                    "cohorte_id": str(e.cohorte_id),
                    "tipo": e.tipo,
                    "numero": e.numero,
                    "periodo": e.periodo,
                    "fecha": e.fecha.isoformat(),
                    "titulo": e.titulo,
                    "created_at": e.created_at.isoformat(),
                    "updated_at": e.updated_at.isoformat(),
                }
                for e in items
            ],
            "total": len(items),
        }

    async def editar(
        self, db: AsyncSession, id: uuid.UUID, data: FechaAcademicaUpdateRequest
    ) -> dict:
        update_data = data.model_dump(exclude_unset=True)
        entity = await self._repo.update(db, id, update_data)
        return {"id": str(entity.id)}

    async def eliminar(self, db: AsyncSession, id: uuid.UUID) -> None:
        await self._repo.soft_delete(db, id)

    async def generar_fragmento_lms(
        self, db: AsyncSession, materia_id: uuid.UUID, cohorte_id: uuid.UUID
    ) -> dict:
        items = await self._repo.get_by_materia_cohorte(db, materia_id, cohorte_id)
        if not items:
            return {"html": "<p>No hay fechas académicas registradas</p>"}

        rows = []
        for e in items:
            rows.append(
                f"<tr>"
                f"<td>{e.tipo}</td>"
                f"<td>{e.numero}</td>"
                f"<td>{e.fecha.isoformat()}</td>"
                f"<td>{e.titulo}</td>"
                f"</tr>"
            )
        html = (
            '<table class="fechas-academicas">'
            "<thead><tr><th>Tipo</th><th>N°</th><th>Fecha</th><th>Título</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )
        return {"html": html}
