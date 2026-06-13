import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.comunicacion import (
    ComunicacionListResponse,
    ComunicacionResponse,
    CrearComunicacionRequest,
    LoteResponse,
    PreviewRequest,
    PreviewResponse,
)
from app.services.comunicacion_service import ComunicacionService

router = APIRouter(prefix="/api/comunicaciones", tags=["comunicaciones"])


@router.post("/preview", response_model=PreviewResponse)
async def preview_comunicacion(
    body: PreviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:enviar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    try:
        return await svc.preview(
            uuid.UUID(body.materia_id),
            body.destinatario_email,
            body.asunto_template,
            body.cuerpo_template,
            db,
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/enviar", status_code=status.HTTP_201_CREATED)
async def enviar_comunicacion(
    body: CrearComunicacionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:enviar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    try:
        result = await svc.enviar(
            uuid.UUID(body.materia_id),
            body.destinatarios,
            body.asunto_template,
            body.cuerpo_template,
            current_user.id,
            db,
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("", response_model=ComunicacionListResponse)
async def listar_comunicaciones(
    lote_id: str | None = Query(None),
    materia_id: str | None = Query(None),
    estado: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:enviar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    return await svc.listar(
        db,
        lote_id=uuid.UUID(lote_id) if lote_id else None,
        materia_id=uuid.UUID(materia_id) if materia_id else None,
        estado=estado,
        pagina=pagina,
        por_pagina=por_pagina,
    )


@router.get("/lotes", response_model=list[LoteResponse])
async def listar_lotes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:enviar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    return await svc.listar_lotes(db)


@router.get("/{id}", response_model=ComunicacionResponse)
async def obtener_comunicacion(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:enviar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    result = await svc.obtener(uuid.UUID(id), db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comunicación no encontrada",
        )
    return result


@router.post("/{id}/cancelar")
async def cancelar_comunicacion(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:enviar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    try:
        result = await svc.cancelar(uuid.UUID(id), current_user.id, db)
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/lote/{lote_id}/aprobar")
async def aprobar_lote(
    lote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:aprobar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    result = await svc.aprobar_lote(uuid.UUID(lote_id), current_user.id, db)
    await db.commit()
    return result


@router.post("/lote/{lote_id}/rechazar")
async def rechazar_lote(
    lote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:aprobar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    result = await svc.rechazar_lote(uuid.UUID(lote_id), current_user.id, db)
    await db.commit()
    return result


@router.post("/{id}/aprobar")
async def aprobar_comunicacion(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("comunicaciones:aprobar")),
):
    svc = ComunicacionService(current_user.tenant_id)
    try:
        result = await svc.aprobar_comunicacion(uuid.UUID(id), current_user.id, db)
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )
