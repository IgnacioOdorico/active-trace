import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.asignacion import Asignacion
from app.models.materia import Materia
from app.models.user import User
from app.schemas.umbral import UmbralUpdateRequest
from app.services.umbral_service import UmbralService

router = APIRouter(prefix="/api/umbral", tags=["umbral"])


async def _find_asignacion(
    db: AsyncSession, materia_id: uuid.UUID, current_user: User
) -> Asignacion | None:
    result = await db.execute(
        select(Asignacion).where(
            Asignacion.tenant_id == current_user.tenant_id,
            Asignacion.materia_id == materia_id,
            Asignacion.usuario_id == current_user.id,
            Asignacion.deleted_at.is_(None),
        )
    )
    return result.unique().scalar_one_or_none()


async def _get_materia_nombre(
    db: AsyncSession, materia_id: uuid.UUID, tenant_id: uuid.UUID
) -> str:
    result = await db.execute(
        select(Materia).where(
            Materia.id == materia_id,
            Materia.tenant_id == tenant_id,
            Materia.deleted_at.is_(None),
        )
    )
    materia = result.unique().scalar_one_or_none()
    return materia.nombre if materia else ""


@router.get("")
async def obtener_umbral(
    materia_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    asignacion = await _find_asignacion(db, materia_id, current_user)
    if not asignacion:
        nombre = await _get_materia_nombre(db, materia_id, current_user.tenant_id)
        return {
            "umbral_pct": 60,
            "valores_aprobatorios": [],
            "es_default": True,
            "materia_id": str(materia_id),
            "materia_nombre": nombre,
        }

    svc = UmbralService(current_user.tenant_id)
    vigente = await svc.obtener_vigente(db, asignacion.id)
    nombre = await _get_materia_nombre(db, materia_id, current_user.tenant_id)

    return {
        "umbral_pct": vigente["umbral_pct"],
        "valores_aprobatorios": vigente["valores_aprobatorios"] or [],
        "es_default": not vigente["es_configurado"],
        "materia_id": str(materia_id),
        "materia_nombre": nombre,
    }


@router.put("")
async def configurar_umbral(
    body: UmbralUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("calificaciones:importar")),
):
    materia_id = uuid.UUID(body.materia_id)
    asignacion = await _find_asignacion(db, materia_id, current_user)
    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una asignación activa para esta materia",
        )

    svc = UmbralService(current_user.tenant_id)
    try:
        umbral_pct = body.umbral_pct if body.umbral_pct is not None else 60.0
        result = await svc.configurar(
            db,
            asignacion_id=asignacion.id,
            materia_id=materia_id,
            umbral_pct=umbral_pct,
            valores_aprobatorios=body.valores_aprobatorios,
        )
        await db.commit()
        return {
            "umbral_pct": result["umbral_pct"],
            "valores_aprobatorios": result["valores_aprobatorios"] or [],
            "recalculo_count": result.get("recalculo_aprobados", 0),
            "mensaje": "Umbral configurado correctamente",
        }
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )
