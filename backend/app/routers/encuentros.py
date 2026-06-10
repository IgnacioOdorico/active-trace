import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.encuentro import (
    CrearEncuentroUnicoRequest,
    CrearSlotRecurrenteRequest,
    EditarInstanciaRequest,
    GenerarHTMLResponse,
    InstanciaEncuentroListResponse,
)
from app.services.encuentro_service import EncuentroService

router = APIRouter(prefix="/api/encuentros", tags=["encuentros"])


@router.post("/slots", response_model=dict)
async def crear_slot_recurrente(
    body: CrearSlotRecurrenteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = EncuentroService(current_user.tenant_id)
    try:
        result = await svc.crear_slot_recurrente(
            body.model_dump(), current_user.id, db
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/instancias", response_model=dict)
async def crear_encuentro_unico(
    body: CrearEncuentroUnicoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = EncuentroService(current_user.tenant_id)
    try:
        result = await svc.crear_encuentro_unico(
            body.model_dump(), current_user.id, db
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.patch("/instancias/{id}", response_model=dict)
async def editar_instancia(
    id: str,
    body: EditarInstanciaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = EncuentroService(current_user.tenant_id)
    try:
        result = await svc.editar_instancia(
            uuid.UUID(id), body.model_dump(exclude_none=True), current_user.id, db
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


@router.get("/html/{materia_id}", response_model=GenerarHTMLResponse)
async def generar_html_encuentros(
    materia_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = EncuentroService(current_user.tenant_id)
    return await svc.generar_html(uuid.UUID(materia_id), db)


@router.get("/instancias", response_model=InstanciaEncuentroListResponse)
async def listar_encuentros(
    materia_id: str | None = Query(None),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    estado: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("encuentros:gestionar")),
):
    svc = EncuentroService(current_user.tenant_id)
    filtros = {
        "materia_id": materia_id,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "estado": estado,
    }
    return await svc.listar(filtros, pagina=pagina, page_size=page_size, db=db)
