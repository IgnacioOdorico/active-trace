import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.padron import (
    ConfirmImportResponse,
    ImportPreviewResponse,
)
from app.services.padron_service import PadronService

router = APIRouter(prefix="/api/padron", tags=["padron"])


@router.post(
    "/importar",
    response_model=ImportPreviewResponse | ConfirmImportResponse,
)
async def importar_padron(
    preview: bool = Query(default=False),
    confirmar: bool = Query(default=False),
    materia_id: str = Query(...),
    cohorte_id: str = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("padron:importar")),
):
    svc = PadronService(current_user.tenant_id)
    content = await file.read()

    try:
        if preview:
            return svc.preview(content, file.filename or "")
        elif confirmar:
            result = await svc.confirm_import(
                db,
                uuid.UUID(materia_id),
                uuid.UUID(cohorte_id),
                content,
                file.filename or "",
                current_user.id,
            )
            await db.commit()
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe especificar preview=true o confirmar=true",
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.delete(
    "/materia/{materia_id}/vaciar",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def vaciar_materia(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("padron:importar")),
):
    svc = PadronService(current_user.tenant_id)
    await svc.vaciar_materia(db, materia_id, current_user.tenant_id)
    await db.commit()
