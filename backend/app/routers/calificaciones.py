import json
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.materia import Materia
from app.models.user import User
from app.schemas.calificacion import (
    ImportPreviewResponse,
    ImportResponse,
    ReporteFinalizacionResponse,
)
from app.services.calificacion_service import CalificacionService

router = APIRouter(prefix="/api/calificaciones", tags=["calificaciones"])


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_calificaciones(
    materia_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = CalificacionService(current_user.tenant_id)
    content = await file.read()

    # Resolve materia info for the response
    materia_nombre = ""
    result = await db.execute(
        select(Materia).where(
            Materia.id == uuid.UUID(materia_id),
            Materia.deleted_at.is_(None),
        )
    )
    materia = result.unique().scalar_one_or_none()
    if materia:
        materia_nombre = materia.nombre

    try:
        preview = svc.preview(content, file.filename or "")
        return {
            "actividades": preview["actividades"],
            "preview": preview["preview"],
            "total_filas": preview["total_filas"],
            "materia_id": materia_id,
            "materia_nombre": materia_nombre,
        }
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/importar", response_model=ImportResponse)
async def importar_calificaciones(
    materia_id: str = Form(...),
    actividad_ids: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = CalificacionService(current_user.tenant_id)
    content = await file.read()

    try:
        actividades = json.loads(actividad_ids)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="actividad_ids debe ser un array JSON de strings",
        )

    if not isinstance(actividades, list) or not all(
        isinstance(a, str) for a in actividades
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="actividad_ids debe ser un array JSON de strings",
        )

    try:
        result = await svc.importar(
            db=db,
            materia_id=uuid.UUID(materia_id),
            actividades=actividades,
            content=content,
            filename=file.filename or "",
            usuario_id=current_user.id,
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/reporte-finalizacion", response_model=ReporteFinalizacionResponse)
async def reporte_finalizacion(
    materia_id: str = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = CalificacionService(current_user.tenant_id)
    content = await file.read()

    try:
        result = await svc.reporte_finalizacion(
            db,
            uuid.UUID(materia_id),
            content,
            file.filename or "",
        )
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )
