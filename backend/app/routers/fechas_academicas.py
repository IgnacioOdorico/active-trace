import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.fecha_academica import (
    FechaAcademicaCreateRequest,
    FechaAcademicaListResponse,
    FechaAcademicaUpdateRequest,
    FragmentoLMSResponse,
)
from app.services.fecha_academica_service import FechaAcademicaService

router = APIRouter(prefix="/api/fechas-academicas", tags=["fechas-academicas"])


@router.post("", response_model=dict)
async def crear_fecha_academica(
    body: FechaAcademicaCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = FechaAcademicaService(current_user.tenant_id)
    try:
        result = await svc.crear(db, body)
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("", response_model=FechaAcademicaListResponse)
async def listar_fechas_academicas(
    materia_id: str | None = Query(None),
    cohorte_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = FechaAcademicaService(current_user.tenant_id)
    return await svc.listar(
        db,
        materia_id=uuid.UUID(materia_id) if materia_id else None,
        cohorte_id=uuid.UUID(cohorte_id) if cohorte_id else None,
    )


@router.get("/{id}", response_model=dict)
async def obtener_fecha_academica(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = FechaAcademicaService(current_user.tenant_id)
    try:
        return await svc.obtener(db, uuid.UUID(id))
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.patch("/{id}", response_model=dict)
async def editar_fecha_academica(
    id: str,
    body: FechaAcademicaUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = FechaAcademicaService(current_user.tenant_id)
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
async def eliminar_fecha_academica(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = FechaAcademicaService(current_user.tenant_id)
    await svc.eliminar(db, uuid.UUID(id))
    await db.commit()


@router.get("/lms/{materia_id}/{cohorte_id}", response_model=FragmentoLMSResponse)
async def generar_fragmento_lms(
    materia_id: str,
    cohorte_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = FechaAcademicaService(current_user.tenant_id)
    return await svc.generar_fragmento_lms(
        db, uuid.UUID(materia_id), uuid.UUID(cohorte_id)
    )
