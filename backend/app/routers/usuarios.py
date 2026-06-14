import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.usuarios import (
    UsuarioCreate,
    UsuarioList,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/admin/usuarios", tags=["usuarios"])


def _to_response(user: User) -> UsuarioResponse:
    return UsuarioResponse(
        id=str(user.id),
        tenant_id=str(user.tenant_id),
        nombre=user.nombre,
        apellidos=user.apellidos,
        email=user.email,
        dni=user.dni,
        cuil=user.cuil,
        cbu=user.cbu,
        alias_cbu=user.alias_cbu,
        banco=user.banco,
        regional=user.regional,
        legajo=user.legajo,
        legajo_profesional=user.legajo_profesional,
        facturador=user.facturador,
        estado=user.estado,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=UsuarioList)
async def list_usuarios(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    estado: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("usuarios:gestionar")),
):
    svc = UsuarioService(current_user.tenant_id)
    users, total = await svc.get_all(db, page=page, page_size=page_size, estado=estado)
    return UsuarioList(
        data=[_to_response(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    body: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("usuarios:gestionar")),
):
    svc = UsuarioService(current_user.tenant_id)
    try:
        user = await svc.create(db, body)
    except DomainError as e:
        if e.detail == "EMAIL_DUPLICADO":
            raise HTTPException(status_code=409, detail="EMAIL_DUPLICADO")
        raise HTTPException(status_code=400, detail=e.detail)
    await db.commit()
    await db.refresh(user)
    return _to_response(user)


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: uuid.UUID,
    body: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("usuarios:gestionar")),
):
    svc = UsuarioService(current_user.tenant_id)
    try:
        user = await svc.update(db, usuario_id, body)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Usuario not found")
    except DomainError as e:
        if e.detail == "EMAIL_DUPLICADO":
            raise HTTPException(status_code=409, detail="EMAIL_DUPLICADO")
        raise HTTPException(status_code=400, detail=e.detail)
    await db.commit()
    await db.refresh(user)
    return _to_response(user)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("usuarios:gestionar")),
):
    svc = UsuarioService(current_user.tenant_id)
    await svc.soft_delete(db, usuario_id)
    await db.commit()
