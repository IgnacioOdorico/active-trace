from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.perfil import PerfilResponse, PerfilUpdate
from app.services.perfil_service import PerfilService

router = APIRouter(prefix="/api/perfil", tags=["perfil"])


@router.get("", response_model=PerfilResponse)
async def obtener_perfil(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("perfil:editar")),
):
    svc = PerfilService(current_user.tenant_id)
    return await svc.obtener(db, current_user)


@router.put("", response_model=PerfilResponse)
async def actualizar_perfil(
    body: PerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("perfil:editar")),
):
    svc = PerfilService(current_user.tenant_id)
    try:
        result = await svc.actualizar(db, current_user, body)
        await db.commit()
        return result
    except DomainError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.detail,
        )
