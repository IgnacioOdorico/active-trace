import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.calificacion import Calificacion
from app.models.user import User
from app.schemas.calificacion import (
    ImportPreviewResponse,
    ImportRequest,
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

    try:
        return svc.preview(content, file.filename or "")
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/importar", response_model=ImportResponse)
async def importar_calificaciones(
    body: ImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = CalificacionService(current_user.tenant_id)
    materia_id = uuid.UUID(body.materia_id)

    try:
        from datetime import datetime, timezone

        affected = 0
        for actividad_id in body.actividad_ids:
            stmt = (
                select(Calificacion)
                .where(
                    Calificacion.tenant_id == current_user.tenant_id,
                    Calificacion.materia_id == materia_id,
                    Calificacion.nombre_actividad == actividad_id,
                    Calificacion.deleted_at.is_(None),
                )
            )
            result = await db.execute(stmt)
            califs = list(result.unique().scalars().all())

            for c in califs:
                if c.nota_numerica is not None and c.nota_numerica >= 60:
                    c.aprobado = True
                elif c.nota_numerica is not None:
                    c.aprobado = False
                c.origen = "Importado"
                c.importado_at = datetime.now(timezone.utc)
                affected += 1

        await db.commit()

        return {
            "insertadas": 0,
            "actualizadas": affected,
            "filas_afectadas": affected,
            "errores": [],
            "advertencias": [],
        }
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
