import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.guardia import (
    CrearGuardiaRequest,
    EditarGuardiaRequest,
    ExportGuardiasResponse,
    GuardiaListResponse,
)
from app.services.guardia_service import GuardiaService

router = APIRouter(prefix="/api/guardias", tags=["guardias"])


@router.post("", response_model=dict)
async def crear_guardia(
    body: CrearGuardiaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = GuardiaService(current_user.tenant_id)
    try:
        result = await svc.crear(
            body.model_dump(), current_user.id, current_user.id, db
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("", response_model=GuardiaListResponse)
async def listar_guardias(
    materia_id: str | None = Query(None),
    asignacion_id: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = GuardiaService(current_user.tenant_id)

    if asignacion_id:
        return await svc.listar_mis_guardias(
            uuid.UUID(asignacion_id), pagina=pagina, page_size=page_size, db=db
        )

    filtros = {
        "materia_id": materia_id,
        "asignacion_id": asignacion_id,
    }
    return await svc.listar_todas(filtros, pagina=pagina, page_size=page_size, db=db)


@router.patch("/{id}", response_model=dict)
async def editar_guardia(
    id: str,
    body: EditarGuardiaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = GuardiaService(current_user.tenant_id)
    try:
        result = await svc.editar(
            uuid.UUID(id), body.model_dump(exclude_none=True), db
        )
        await db.commit()
        return result
    except DomainError as e:
        if "no encontrada" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.detail,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("/exportar", response_model=ExportGuardiasResponse)
async def exportar_guardias(
    materia_id: str | None = Query(None),
    asignacion_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = GuardiaService(current_user.tenant_id)
    filtros = {
        "materia_id": materia_id,
        "asignacion_id": asignacion_id,
    }
    return await svc.exportar(filtros, db)
