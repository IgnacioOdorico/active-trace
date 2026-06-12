import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.programa import (
    ProgramaMateriaCreateRequest,
    ProgramaMateriaListResponse,
    ProgramaMateriaUpdateRequest,
)
from app.services.programa_service import ProgramaService

router = APIRouter(prefix="/api/programas", tags=["programas"])


@router.post("", response_model=dict)
async def crear_programa(
    body: ProgramaMateriaCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = ProgramaService(current_user.tenant_id)
    try:
        result = await svc.crear(db, body)
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("", response_model=ProgramaMateriaListResponse)
async def listar_programas(
    materia_id: str | None = Query(None),
    carrera_id: str | None = Query(None),
    cohorte_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = ProgramaService(current_user.tenant_id)
    return await svc.listar(
        db,
        materia_id=uuid.UUID(materia_id) if materia_id else None,
        carrera_id=uuid.UUID(carrera_id) if carrera_id else None,
        cohorte_id=uuid.UUID(cohorte_id) if cohorte_id else None,
    )


@router.get("/{id}", response_model=dict)
async def obtener_programa(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = ProgramaService(current_user.tenant_id)
    try:
        return await svc.obtener(db, uuid.UUID(id))
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.patch("/{id}", response_model=dict)
async def editar_programa(
    id: str,
    body: ProgramaMateriaUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = ProgramaService(current_user.tenant_id)
    try:
        result = await svc.editar(db, uuid.UUID(id), body)
        await db.commit()
        return result
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_programa(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = ProgramaService(current_user.tenant_id)
    await svc.eliminar(db, uuid.UUID(id))
    await db.commit()
