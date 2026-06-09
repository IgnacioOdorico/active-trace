import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.umbral import UmbralConfigRequest, UmbralMateriaResponse
from app.services.umbral_service import UmbralService

router = APIRouter(prefix="/api/umbral", tags=["umbral"])


@router.put("/{asignacion_id}", response_model=UmbralMateriaResponse)
async def configurar_umbral(
    asignacion_id: uuid.UUID,
    body: UmbralConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = UmbralService(current_user.tenant_id)
    try:
        result = await svc.configurar(
            db,
            asignacion_id=asignacion_id,
            materia_id=uuid.UUID(int=0),
            umbral_pct=body.umbral_pct,
            valores_aprobatorios=body.valores_aprobatorios,
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("/{asignacion_id}")
async def obtener_umbral(
    asignacion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    svc = UmbralService(current_user.tenant_id)
    return await svc.obtener_vigente(db, asignacion_id)
