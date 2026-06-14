import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.core.permissions import require_permission
from app.models.asignacion import Asignacion
from app.models.user import User
from app.schemas.asignaciones import (
    AsignacionCreate,
    AsignacionList,
    AsignacionResponse,
    AsignacionUpdate,
)
from app.services.asignacion_service import AsignacionService

router = APIRouter(prefix="/api/asignaciones", tags=["asignaciones"])


def _to_response(a: Asignacion) -> AsignacionResponse:
    return AsignacionResponse(
        id=str(a.id),
        tenant_id=str(a.tenant_id),
        usuario_id=str(a.usuario_id),
        rol=a.rol,
        materia_id=str(a.materia_id) if a.materia_id else None,
        carrera_id=str(a.carrera_id) if a.carrera_id else None,
        cohorte_id=str(a.cohorte_id) if a.cohorte_id else None,
        comisiones=a.comisiones,
        responsable_id=str(a.responsable_id) if a.responsable_id else None,
        desde=a.desde,
        hasta=a.hasta,
        estado_vigencia=a.estado_vigencia,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


@router.get("", response_model=AsignacionList)
async def list_asignaciones(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    usuario_id: str | None = Query(default=None),
    materia_id: str | None = Query(default=None),
    carrera_id: str | None = Query(default=None),
    cohorte_id: str | None = Query(default=None),
    rol: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = AsignacionService(current_user.tenant_id)
    asignaciones, total = await svc.get_all(
        db,
        page=page,
        page_size=page_size,
        usuario_id=usuario_id,
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        rol=rol,
    )
    return AsignacionList(
        data=[_to_response(a) for a in asignaciones],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=AsignacionResponse, status_code=status.HTTP_201_CREATED)
async def create_asignacion(
    body: AsignacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = AsignacionService(current_user.tenant_id)
    asignacion = await svc.create(db, body)
    await db.commit()
    await db.refresh(asignacion)
    return _to_response(asignacion)


@router.patch("/{asignacion_id}", response_model=AsignacionResponse)
async def update_asignacion(
    asignacion_id: uuid.UUID,
    body: AsignacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = AsignacionService(current_user.tenant_id)
    try:
        asignacion = await svc.update(db, asignacion_id, body)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Asignacion not found")
    await db.commit()
    await db.refresh(asignacion)
    return _to_response(asignacion)


@router.delete("/{asignacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asignacion(
    asignacion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = AsignacionService(current_user.tenant_id)
    await svc.soft_delete(db, asignacion_id)
    await db.commit()
