import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.repositories.guardia_repository import GuardiaRepository
from app.services.audit_service import AuditLogService

_TRANSICIONES_GUARDIA: dict[str, set[str]] = {
    "Pendiente": {"Realizada", "Cancelada"},
    "Realizada": {"Realizada"},
    "Cancelada": {"Cancelada"},
}


class GuardiaService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._guardia_repo = GuardiaRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)

    @staticmethod
    def _validar_transicion_estado(actual: str, destino: str) -> None:
        if destino not in _TRANSICIONES_GUARDIA.get(actual, set()):
            raise DomainError(
                f"Transición inválida: {actual} → {destino}"
            )

    async def crear(
        self,
        data: dict,
        usuario_id: uuid.UUID,
        asignacion_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        guardia_data = {
            "asignacion_id": asignacion_id,
            "materia_id": uuid.UUID(str(data["materia_id"])),
            "carrera_id": uuid.UUID(str(data["carrera_id"])),
            "cohorte_id": (
                uuid.UUID(str(data["cohorte_id"]))
                if data.get("cohorte_id") else None
            ),
            "dia": data["dia"],
            "horario": data["horario"],
            "comentarios": data.get("comentarios"),
        }
        guardia = await self._guardia_repo.create(db, guardia_data)

        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.GUARDIA_CREAR,
            materia_id=guardia.materia_id,
            detalle={
                "guardia_id": str(guardia.id),
                "materia_id": str(guardia.materia_id),
                "asignacion_id": str(asignacion_id),
            },
        )

        return {"id": str(guardia.id)}

    async def listar_mis_guardias(
        self,
        asignacion_id: uuid.UUID,
        *,
        pagina: int = 1,
        page_size: int = 50,
        db: AsyncSession,
    ) -> dict:
        page_size = min(page_size, 100)
        todas = await self._guardia_repo.get_by_asignacion(db, asignacion_id)

        total = len(todas)
        offset = (pagina - 1) * page_size
        pagina_items = todas[offset : offset + page_size]

        items = [_serializar_guardia(g) for g in pagina_items]

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    async def listar_todas(
        self,
        filtros: dict,
        *,
        pagina: int = 1,
        page_size: int = 50,
        db: AsyncSession,
    ) -> dict:
        page_size = min(page_size, 100)
        materia_id = filtros.get("materia_id")
        if materia_id is not None:
            materia_id = uuid.UUID(str(materia_id))
        asignacion_id = filtros.get("asignacion_id")
        if asignacion_id is not None:
            asignacion_id = uuid.UUID(str(asignacion_id))

        todas = await self._guardia_repo.get_all_filtros(
            db,
            materia_id=materia_id,
            asignacion_id=asignacion_id,
        )

        total = len(todas)
        offset = (pagina - 1) * page_size
        pagina_items = todas[offset : offset + page_size]

        items = [_serializar_guardia(g) for g in pagina_items]

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    async def editar(
        self,
        guardia_id: uuid.UUID,
        data: dict,
        db: AsyncSession,
    ) -> dict:
        guardia = await self._guardia_repo.get(db, guardia_id)
        if guardia is None:
            raise DomainError(f"Guardia no encontrada: {guardia_id}")

        estado_anterior = guardia.estado
        if data.get("estado") is not None:
            self._validar_transicion_estado(estado_anterior, data["estado"])
            guardia.estado = data["estado"]
        if data.get("comentarios") is not None:
            guardia.comentarios = data["comentarios"]

        await db.flush()
        await db.refresh(guardia)

        return {"id": str(guardia.id), "estado": guardia.estado}

    async def exportar(
        self,
        filtros: dict,
        db: AsyncSession,
    ) -> dict:
        materia_id = filtros.get("materia_id")
        if materia_id is not None:
            materia_id = uuid.UUID(str(materia_id))
        asignacion_id = filtros.get("asignacion_id")
        if asignacion_id is not None:
            asignacion_id = uuid.UUID(str(asignacion_id))

        todas = await self._guardia_repo.get_all_filtros(
            db,
            materia_id=materia_id,
            asignacion_id=asignacion_id,
        )

        items = [_serializar_guardia(g) for g in todas]

        return {"items": items}


def _serializar_guardia(g) -> dict:
    return {
        "id": str(g.id),
        "asignacion_id": str(g.asignacion_id),
        "materia_id": str(g.materia_id),
        "carrera_id": str(g.carrera_id),
        "cohorte_id": str(g.cohorte_id) if g.cohorte_id else None,
        "dia": g.dia,
        "horario": g.horario,
        "estado": g.estado,
        "comentarios": g.comentarios,
    }
