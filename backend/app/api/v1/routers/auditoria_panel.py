import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.permissions import PermissionChecker, decode_access_token
from app.models.asignacion import Asignacion
from app.models.user import User
from app.schemas.audit import AuditLogResponse
from app.schemas.auditoria_panel import (
    AccionesPorDiaItem,
    ComunicacionesPorDocenteItem,
    InteraccionesPorDocenteMateriaItem,
    UltimasAccionesResponse,
)
from app.services.audit_service import AuditLogService

router = APIRouter(prefix="/api/v1/admin/panel", tags=["auditoria-panel"])


async def _resolve_panel_permission(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> tuple[bool, list[uuid.UUID] | None]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = auth.split(" ", 1)[1]
    payload = decode_access_token(token)
    roles: list[str] = payload.get("rols", [])

    if not roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    checker = PermissionChecker(roles, db)
    has_full, _ = await checker.has_permission("auditoria:ver")
    if has_full:
        return True, None

    has_propio, _ = await checker.has_permission("auditoria:ver(propio)")
    if has_propio:
        now = datetime.now()
        result = await db.execute(
            select(Asignacion.materia_id)
            .where(
                Asignacion.usuario_id == current_user.id,
                Asignacion.materia_id.isnot(None),
                Asignacion.desde <= now,
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= now),
            )
        )
        materias_ids = list(set(result.scalars().all()))
        return True, materias_ids if materias_ids else None

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.get("/acciones-por-dia", response_model=list[AccionesPorDiaItem])
async def get_acciones_por_dia(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission: tuple[bool, list[uuid.UUID] | None] = Depends(_resolve_panel_permission),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    materia_id: str | None = Query(None),
    actor_id: str | None = Query(None),
    accion: str | None = Query(None),
):
    _, materias_ids = permission
    svc = AuditLogService(current_user.tenant_id)

    if desde is None:
        desde = datetime.now() - timedelta(days=30)
    if hasta is None:
        hasta = datetime.now()

    materia_uuid = uuid.UUID(materia_id) if materia_id else None
    actor_uuid = uuid.UUID(actor_id) if actor_id else None

    return await svc.acciones_por_dia(
        db,
        desde=desde,
        hasta=hasta,
        materia_id=materia_uuid,
        actor_id=actor_uuid,
        accion=accion,
        materias_ids=materias_ids,
    )


@router.get("/comunicaciones-por-docente", response_model=list[ComunicacionesPorDocenteItem])
async def get_comunicaciones_por_docente(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission: tuple[bool, list[uuid.UUID] | None] = Depends(_resolve_panel_permission),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    materia_id: str | None = Query(None),
):
    _, materias_ids = permission
    svc = AuditLogService(current_user.tenant_id)

    if desde is None:
        desde = datetime.now() - timedelta(days=30)
    if hasta is None:
        hasta = datetime.now()

    materia_uuid = uuid.UUID(materia_id) if materia_id else None

    return await svc.comunicaciones_por_docente(
        db,
        desde=desde,
        hasta=hasta,
        materia_id=materia_uuid,
        materias_ids=materias_ids,
    )


@router.get("/interacciones-por-docente-materia", response_model=list[InteraccionesPorDocenteMateriaItem])
async def get_interacciones_por_docente_materia(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission: tuple[bool, list[uuid.UUID] | None] = Depends(_resolve_panel_permission),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    materia_id: str | None = Query(None),
    actor_id: str | None = Query(None),
):
    _, materias_ids = permission
    svc = AuditLogService(current_user.tenant_id)

    if desde is None:
        desde = datetime.now() - timedelta(days=30)
    if hasta is None:
        hasta = datetime.now()

    materia_uuid = uuid.UUID(materia_id) if materia_id else None
    actor_uuid = uuid.UUID(actor_id) if actor_id else None

    return await svc.interacciones_por_docente_materia(
        db,
        desde=desde,
        hasta=hasta,
        materia_id=materia_uuid,
        actor_id=actor_uuid,
        materias_ids=materias_ids,
    )


@router.get("/ultimas-acciones", response_model=UltimasAccionesResponse)
async def get_ultimas_acciones(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission: tuple[bool, list[uuid.UUID] | None] = Depends(_resolve_panel_permission),
    max: int = Query(200, ge=1, le=1000),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    materia_id: str | None = Query(None),
    actor_id: str | None = Query(None),
    accion: str | None = Query(None),
):
    _, materias_ids = permission
    svc = AuditLogService(current_user.tenant_id)

    if desde is None:
        desde = datetime.now() - timedelta(days=30)
    if hasta is None:
        hasta = datetime.now()

    materia_uuid = uuid.UUID(materia_id) if materia_id else None
    actor_uuid = uuid.UUID(actor_id) if actor_id else None

    items = await svc.ultimas_acciones(
        db,
        max_resultados=max,
        desde=desde,
        hasta=hasta,
        materia_id=materia_uuid,
        actor_id=actor_uuid,
        accion=accion,
        materias_ids=materias_ids,
    )

    return UltimasAccionesResponse(
        items=[
            AuditLogResponse(
                id=str(item.id),
                fecha_hora=item.fecha_hora,
                actor_id=str(item.actor_id),
                impersonado_id=str(item.impersonado_id) if item.impersonado_id else None,
                materia_id=str(item.materia_id) if item.materia_id else None,
                accion=item.accion,
                detalle=item.detalle,
                filas_afectadas=item.filas_afectadas,
                ip=item.ip,
                user_agent=item.user_agent,
            )
            for item in items
        ],
        max_resultados=max,
    )
