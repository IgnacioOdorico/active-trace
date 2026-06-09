import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
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
    materia_id: str = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = CalificacionService(current_user.tenant_id)
    content = await file.read()

    try:
        return svc.preview(content, file.filename or "")
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/importar", response_model=ImportResponse)
async def importar_calificaciones(
    materia_id: str = Form(...),
    actividades: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = CalificacionService(current_user.tenant_id)
    content = await file.read()

    try:
        import json
        actividades_list = json.loads(actividades)
        result = await svc.importar(
            db,
            uuid.UUID(materia_id),
            actividades_list,
            content,
            file.filename or "",
            current_user.id,
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
