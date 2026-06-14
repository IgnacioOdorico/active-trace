import math
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token
from app.core.dependencies import get_current_user, get_db
from app.core.permissions import PermissionChecker, decode_access_token
from app.models.user import User
from app.schemas.audit import (
    AuditLogFilter,
    AuditLogResponse,
    ImpersonationResponse,
    ImpersonationStartRequest,
    PaginatedAuditLogResponse,
)
from app.services.audit_service import IMPERSONACION_FINALIZAR, IMPERSONACION_INICIAR, AuditLogService

router = APIRouter(prefix="/api/v1/admin", tags=["audit"])


async def _resolve_audit_permission(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> tuple[bool, uuid.UUID | None]:
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
        return True, current_user.id

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.get("/audit-log", response_model=PaginatedAuditLogResponse)
async def list_audit_log(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission: tuple[bool, uuid.UUID | None] = Depends(_resolve_audit_permission),
    actor_id: str | None = Query(None),
    materia_id: str | None = Query(None),
    accion: str | None = Query(None),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(50, ge=1, le=200),
):
    can_view_all, own_id = permission
    svc = AuditLogService(current_user.tenant_id)

    actor_uuid = uuid.UUID(actor_id) if actor_id else None
    materia_uuid = uuid.UUID(materia_id) if materia_id else None

    if not can_view_all:
        actor_uuid = own_id

    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    items, total = await svc.list(
        db,
        actor_id=actor_uuid,
        materia_id=materia_uuid,
        accion=accion,
        desde=desde,
        hasta=hasta,
        pagina=pagina,
        por_pagina=por_pagina,
    )

    total_paginas = math.ceil(total / por_pagina) if total > 0 else 0

    return PaginatedAuditLogResponse(
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
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        total_paginas=total_paginas,
    )


async def _require_impersonacion_permission(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = auth.split(" ", 1)[1]
    payload = decode_access_token(token)
    roles: list[str] = payload.get("rols", [])

    if not roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    checker = PermissionChecker(roles, db)
    has_perm, _ = await checker.has_permission("impersonacion:usar")
    if not has_perm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.post("/impersonation/start", response_model=ImpersonationResponse)
async def start_impersonation(
    request: Request,
    body: ImpersonationStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(_require_impersonacion_permission),
):
    target_user_id = uuid.UUID(body.target_user_id)
    target_user = await db.get(User, target_user_id)
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if target_user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no pertenece al mismo tenant")

    if not target_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario objetivo está inactivo")

    auth = request.headers.get("Authorization", "")
    token = auth.split(" ", 1)[1]
    payload = decode_access_token(token)
    original_roles: list[str] = payload.get("rols", [])

    new_token = create_access_token(
        user_id=str(target_user.id),
        tenant_id=str(current_user.tenant_id),
        roles=[],
        impersonating=True,
        impersonator_id=str(current_user.id),
        impersonated_user_id=str(target_user.id),
        original_roles=original_roles,
    )

    svc = AuditLogService(current_user.tenant_id)
    await svc.log(
        db,
        actor_id=current_user.id,
        accion=IMPERSONACION_INICIAR,
        impersonado_id=target_user.id,
        detalle={
            "impersonator_id": str(current_user.id),
            "impersonated_user_id": str(target_user.id),
            "impersonator_email": current_user.email,
            "target_email": target_user.email,
        },
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()

    return ImpersonationResponse(
        access_token=new_token,
        impersonating=True,
    )


@router.post("/impersonation/end", response_model=ImpersonationResponse)
async def end_impersonation(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(_require_impersonacion_permission),
):
    auth = request.headers.get("Authorization", "")
    token = auth.split(" ", 1)[1]
    payload = decode_access_token(token)

    impersonator_id = payload.get("impersonator_id")
    impersonated_user_id = payload.get("impersonated_user_id")

    if not impersonator_id or not impersonated_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay una sesión de impersonación activa")

    original_roles: list[str] = payload.get("original_roles", [])

    impersonator = await db.get(User, uuid.UUID(impersonator_id))
    if impersonator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario impersonador no encontrado")

    new_token = create_access_token(
        user_id=impersonator_id,
        tenant_id=str(current_user.tenant_id),
        roles=original_roles,
    )

    svc = AuditLogService(current_user.tenant_id)
    await svc.log(
        db,
        actor_id=uuid.UUID(impersonator_id),
        accion=IMPERSONACION_FINALIZAR,
        impersonado_id=uuid.UUID(impersonated_user_id),
        detalle={
            "impersonator_id": impersonator_id,
            "impersonated_user_id": impersonated_user_id,
        },
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()

    return ImpersonationResponse(
        access_token=new_token,
        impersonating=False,
    )
