import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.aviso import (
    AvisoCreateRequest,
    AvisoListResponse,
    AvisoResponse,
    AvisoUpdateRequest,
)
from app.services.aviso_service import AvisoService

router = APIRouter(prefix="/api/avisos", tags=["avisos"])


@router.post("", response_model=AvisoResponse, status_code=status.HTTP_201_CREATED)
async def crear_aviso(
    body: AvisoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("avisos:publicar")),
):
    svc = AvisoService(current_user.tenant_id)
    data = body.model_dump()
    # Convert string UUIDs to UUID objects
    if data.get("materia_id"):
        data["materia_id"] = uuid.UUID(data["materia_id"])
    if data.get("cohorte_id"):
        data["cohorte_id"] = uuid.UUID(data["cohorte_id"])
    result = await svc.crear(data, current_user.id, db)
    await db.commit()
    return result


@router.get("", response_model=AvisoListResponse)
async def listar_avisos_visibles(
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = AvisoService(current_user.tenant_id)
    return await svc.listar_visibles(
        current_user, db, pagina=pagina, page_size=page_size
    )


@router.get("/gestion", response_model=AvisoListResponse)
async def listar_avisos_gestion(
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("avisos:publicar")),
):
    svc = AvisoService(current_user.tenant_id)
    return await svc.listar_gestion(db, pagina=pagina, page_size=page_size)


@router.get("/{id}", response_model=AvisoResponse)
async def obtener_aviso(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("avisos:publicar")),
):
    svc = AvisoService(current_user.tenant_id)
    result = await svc.obtener(uuid.UUID(id), db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso no encontrado",
        )
    return result


@router.patch("/{id}", response_model=AvisoResponse)
async def editar_aviso(
    id: str,
    body: AvisoUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("avisos:publicar")),
):
    svc = AvisoService(current_user.tenant_id)
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    if "materia_id" in data and data["materia_id"]:
        data["materia_id"] = uuid.UUID(data["materia_id"])
    if "cohorte_id" in data and data["cohorte_id"]:
        data["cohorte_id"] = uuid.UUID(data["cohorte_id"])
    try:
        result = await svc.editar(uuid.UUID(id), data, current_user.id, db)
        await db.commit()
        return result
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso no encontrado",
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_aviso(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("avisos:publicar")),
):
    svc = AvisoService(current_user.tenant_id)
    try:
        await svc.eliminar(uuid.UUID(id), current_user.id, db)
        await db.commit()
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso no encontrado",
        )


@router.post("/{id}/ack")
async def confirmar_lectura(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = AvisoService(current_user.tenant_id)
    try:
        result = await svc.confirmar_lectura(
            uuid.UUID(id), current_user.id, db
        )
        await db.commit()
        return result
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso no encontrado",
        )
