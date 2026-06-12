import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.services.inbox_service import InboxService


class ResponderRequest(BaseModel):
    cuerpo: str


router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("")
async def listar_hilos(
    pagina: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("inbox:leer")),
):
    svc = InboxService(current_user.tenant_id)
    items, total = await svc.listar_hilos(
        db, current_user.id, pagina=pagina, page_size=page_size
    )
    return {"items": items, "total": total, "pagina": pagina, "page_size": page_size}


@router.get("/{hilo_id}")
async def obtener_hilo(
    hilo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("inbox:leer")),
):
    svc = InboxService(current_user.tenant_id)
    try:
        return await svc.obtener_hilo(db, current_user.id, hilo_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hilo no encontrado")


@router.post("/{hilo_id}/responder", status_code=status.HTTP_201_CREATED)
async def responder_hilo(
    hilo_id: uuid.UUID,
    body: ResponderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("inbox:responder")),
):
    svc = InboxService(current_user.tenant_id)
    try:
        result = await svc.responder(db, current_user.id, hilo_id, body.cuerpo)
        await db.commit()
        return result
    except EntityNotFoundError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hilo no encontrado")
