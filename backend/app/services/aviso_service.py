import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.acknowledgment_aviso_repository import (
    AcknowledgmentAvisoRepository,
)
from app.repositories.aviso_repository import AvisoRepository
from app.services.audit_service import AuditLogService


class AvisoService:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self._aviso_repo = AvisoRepository(tenant_id)
        self._ack_repo = AcknowledgmentAvisoRepository(tenant_id)
        self._audit_service = AuditLogService(tenant_id)
        self._tenant_id = tenant_id

    async def _obtener_asignaciones_usuario(
        self, db: AsyncSession, usuario_id: uuid.UUID
    ) -> tuple[list[uuid.UUID], list[uuid.UUID]]:
        from app.models.asignacion import Asignacion
        from sqlalchemy import select

        now = datetime.now(timezone.utc)
        query = select(Asignacion).where(
            Asignacion.tenant_id == self._tenant_id,
            Asignacion.deleted_at.is_(None),
            Asignacion.usuario_id == usuario_id,
            Asignacion.desde <= now,
        )
        result = await db.execute(query)
        asignaciones = list(result.unique().scalars().all())

        materia_ids = list({
            a.materia_id for a in asignaciones
            if a.materia_id is not None
        })
        cohorte_ids = list({
            a.cohorte_id for a in asignaciones
            if a.cohorte_id is not None
        })
        return materia_ids, cohorte_ids

    async def crear(
        self, data: dict, usuario_id: uuid.UUID, db: AsyncSession
    ) -> dict:
        aviso = await self._aviso_repo.create(db, data)
        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.AVISO_PUBLICAR,
            detalle={
                "aviso_id": str(aviso.id),
                "titulo": aviso.titulo,
            },
        )
        return self._serializar(aviso)

    async def editar(
        self,
        aviso_id: uuid.UUID,
        data: dict,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        aviso = await self._aviso_repo.update(db, aviso_id, data)
        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.AVISO_EDITAR,
            detalle={
                "aviso_id": str(aviso.id),
                "campos_modificados": list(data.keys()),
            },
        )
        return self._serializar(aviso)

    async def eliminar(
        self,
        aviso_id: uuid.UUID,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> None:
        aviso = await self._aviso_repo.get_with_deleted(db, aviso_id)
        if aviso is None or aviso.deleted_at is not None:
            from app.core.exceptions import EntityNotFoundError
            raise EntityNotFoundError("Aviso", aviso_id)
        await self._aviso_repo.soft_delete(db, aviso_id)
        await self._audit_service.log(
            db,
            actor_id=usuario_id,
            accion=AuditLogService.AVISO_ELIMINAR,
            detalle={
                "aviso_id": str(aviso_id),
                "titulo": aviso.titulo,
            },
        )

    async def listar_visibles(
        self,
        usuario: User,
        db: AsyncSession,
        pagina: int = 1,
        page_size: int = 50,
    ) -> dict:
        materia_ids, cohorte_ids = await self._obtener_asignaciones_usuario(
            db, usuario.id
        )
        roles = [r.codigo for r in usuario.roles] if hasattr(usuario, "roles") and usuario.roles else []

        items, total = await self._aviso_repo.list_visibles(
            db,
            usuario_id=usuario.id,
            roles=roles,
            materia_ids=materia_ids,
            cohorte_ids=cohorte_ids,
            pagina=pagina,
            page_size=page_size,
        )

        return {
            "items": [self._serializar(a) for a in items],
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    async def listar_gestion(
        self,
        db: AsyncSession,
        pagina: int = 1,
        page_size: int = 50,
    ) -> dict:
        items, total = await self._aviso_repo.list_gestion(
            db, pagina=pagina, page_size=page_size
        )

        result = []
        for a in items:
            d = self._serializar(a)
            d["total_acks"] = await self._ack_repo.contar_por_aviso(db, a.id)
            result.append(d)

        return {
            "items": result,
            "total": total,
            "pagina": pagina,
            "page_size": page_size,
        }

    async def obtener(
        self,
        aviso_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict | None:
        aviso = await self._aviso_repo.get_with_deleted(db, aviso_id)
        if aviso is None or aviso.deleted_at is not None:
            return None
        d = self._serializar(aviso)
        d["total_acks"] = await self._ack_repo.contar_por_aviso(db, aviso_id)
        return d

    async def confirmar_lectura(
        self,
        aviso_id: uuid.UUID,
        usuario_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        aviso = await self._aviso_repo.get_with_deleted(db, aviso_id)
        if aviso is None or aviso.deleted_at is not None:
            from app.core.exceptions import EntityNotFoundError
            raise EntityNotFoundError("Aviso", aviso_id)

        existe = await self._ack_repo.existe(db, aviso_id, usuario_id)
        if not existe:
            ack = await self._ack_repo.crear(db, aviso_id, usuario_id)
            return {
                "id": str(ack.id),
                "aviso_id": str(ack.aviso_id),
                "usuario_id": str(ack.usuario_id),
                "confirmado_at": ack.confirmado_at.isoformat(),
            }

        return {
            "id": "",
            "aviso_id": str(aviso_id),
            "usuario_id": str(usuario_id),
            "confirmado_at": "",
        }

    @staticmethod
    def _serializar(aviso) -> dict:
        return {
            "id": str(aviso.id),
            "tenant_id": str(aviso.tenant_id),
            "alcance": aviso.alcance,
            "materia_id": str(aviso.materia_id) if aviso.materia_id else None,
            "cohorte_id": str(aviso.cohorte_id) if aviso.cohorte_id else None,
            "rol_destino": aviso.rol_destino,
            "severidad": aviso.severidad,
            "titulo": aviso.titulo,
            "cuerpo": aviso.cuerpo,
            "inicio_en": aviso.inicio_en.isoformat() if aviso.inicio_en else None,
            "fin_en": aviso.fin_en.isoformat() if aviso.fin_en else None,
            "orden": aviso.orden,
            "activo": aviso.activo,
            "requiere_ack": aviso.requiere_ack,
            "created_at": aviso.created_at.isoformat() if aviso.created_at else None,
            "updated_at": aviso.updated_at.isoformat() if aviso.updated_at else None,
            "total_acks": 0,
        }
