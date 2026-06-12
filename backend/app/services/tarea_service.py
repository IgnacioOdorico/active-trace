import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError, EntityNotFoundError
from app.models.tarea import EstadoTarea, Tarea
from app.repositories.comentario_tarea_repository import ComentarioTareaRepository
from app.repositories.tarea_repository import TareaRepository
from app.services.audit_service import AuditLogService

_TRANSICIONES: dict[EstadoTarea, set[EstadoTarea]] = {
    EstadoTarea.Pendiente: {EstadoTarea.En_progreso, EstadoTarea.Cancelada},
    EstadoTarea.En_progreso: {EstadoTarea.Resuelta, EstadoTarea.Cancelada},
    EstadoTarea.Resuelta: set(),
    EstadoTarea.Cancelada: set(),
}


def _validar_transicion(desde: str, hasta: str) -> None:
    if desde == hasta:
        return
    try:
        desde_enum = EstadoTarea(desde)
        hasta_enum = EstadoTarea(hasta)
    except ValueError:
        raise DomainError(f"Estado inválido: {desde} → {hasta}")

    permitidos = _TRANSICIONES.get(desde_enum, set())
    if hasta_enum not in permitidos:
        raise DomainError(
            f"Transición de estado no permitida: {desde} → {hasta}"
        )


class TareaService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._tarea_repo = TareaRepository(tenant_id)
        self._comentario_repo = ComentarioTareaRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)
        self._tenant_id = tenant_id

    async def crear(
        self, data: dict, usuario_id: uuid.UUID, db: AsyncSession
    ) -> dict:
        data["asignado_por"] = usuario_id
        data["estado"] = EstadoTarea.Pendiente
        tarea = await self._tarea_repo.create(db, data)
        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.TAREA_CREAR,
            detalle={
                "tarea_id": str(tarea.id),
                "asignado_a": str(tarea.asignado_a),
                "asignado_por": str(tarea.asignado_por),
            },
        )
        return self._serializar(tarea)

    async def editar(
        self,
        tarea_id: uuid.UUID,
        data: dict,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        tarea = await self._tarea_repo.get(db, tarea_id)
        if tarea is None:
            raise EntityNotFoundError("Tarea", tarea_id)

        if "estado" in data and data["estado"] != tarea.estado:
            _validar_transicion(tarea.estado, data["estado"])

        tarea = await self._tarea_repo.update(db, tarea_id, data)
        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.TAREA_EDITAR,
            detalle={
                "tarea_id": str(tarea.id),
                "campos_modificados": list(data.keys()),
            },
        )
        return self._serializar(tarea)

    async def eliminar(
        self,
        tarea_id: uuid.UUID,
        db: AsyncSession,
    ) -> None:
        tarea = await self._tarea_repo.get(db, tarea_id)
        if tarea is None:
            raise EntityNotFoundError("Tarea", tarea_id)
        await self._tarea_repo.soft_delete(db, tarea_id)

    async def listar_mias(
        self,
        usuario_id: uuid.UUID,
        estado: str | None,
        pagina: int,
        page_size: int,
        db: AsyncSession,
    ) -> dict:
        items, total = await self._tarea_repo.list_mias(
            db, usuario_id=usuario_id, estado=estado, pagina=pagina, page_size=page_size
        )
        return {
            "items": [self._serializar(t) for t in items],
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    async def listar_todas(
        self,
        asignado_a: uuid.UUID | None,
        asignado_por: uuid.UUID | None,
        materia_id: uuid.UUID | None,
        estado: str | None,
        busqueda: str | None,
        pagina: int,
        page_size: int,
        db: AsyncSession,
    ) -> dict:
        items, total = await self._tarea_repo.list_todas(
            db,
            asignado_a=asignado_a,
            asignado_por=asignado_por,
            materia_id=materia_id,
            estado=estado,
            busqueda=busqueda,
            pagina=pagina,
            page_size=page_size,
        )
        return {
            "items": [self._serializar(t) for t in items],
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    async def obtener(
        self,
        tarea_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict | None:
        tarea = await self._tarea_repo.get(db, tarea_id)
        if tarea is None:
            return None
        return self._serializar(tarea)

    async def agregar_comentario(
        self,
        tarea_id: uuid.UUID,
        texto: str,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        tarea = await self._tarea_repo.get(db, tarea_id)
        if tarea is None:
            raise EntityNotFoundError("Tarea", tarea_id)

        comentario = await self._comentario_repo.create(
            db,
            {
                "tarea_id": tarea_id,
                "autor_id": usuario_id,
                "texto": texto,
            },
        )
        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.TAREA_COMENTAR,
            detalle={
                "tarea_id": str(tarea_id),
                "comentario_id": str(comentario.id),
            },
        )
        return {
            "id": str(comentario.id),
            "tarea_id": str(comentario.tarea_id),
            "autor_id": str(comentario.autor_id),
            "texto": comentario.texto,
            "creado_at": comentario.creado_at.isoformat() if comentario.creado_at else None,
        }

    async def listar_comentarios(
        self,
        tarea_id: uuid.UUID,
        pagina: int,
        page_size: int,
        db: AsyncSession,
    ) -> dict:
        items, total = await self._comentario_repo.list_por_tarea(
            db, tarea_id=tarea_id, pagina=pagina, page_size=page_size
        )
        return {
            "items": [
                {
                    "id": str(c.id),
                    "tarea_id": str(c.tarea_id),
                    "autor_id": str(c.autor_id),
                    "texto": c.texto,
                    "creado_at": c.creado_at.isoformat() if c.creado_at else None,
                }
                for c in items
            ],
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    @staticmethod
    def _serializar(tarea: Tarea) -> dict:
        return {
            "id": str(tarea.id),
            "tenant_id": str(tarea.tenant_id),
            "materia_id": str(tarea.materia_id) if tarea.materia_id else None,
            "asignado_a": str(tarea.asignado_a),
            "asignado_por": str(tarea.asignado_por),
            "estado": tarea.estado,
            "descripcion": tarea.descripcion,
            "contexto_id": str(tarea.contexto_id) if tarea.contexto_id else None,
            "created_at": tarea.created_at.isoformat() if tarea.created_at else None,
            "updated_at": tarea.updated_at.isoformat() if tarea.updated_at else None,
        }
