import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.equipos import (
    AsignacionMasivaRequest,
    AsignacionMasivaResponse,
    ClonarRequest,
    ClonarResponse,
    EquipoItemResponse,
    EquipoListResponse,
    VigenciaMasivaRequest,
    VigenciaMasivaResponse,
    VigenciaRequest,
)
from app.services.equipo_service import EquipoService

router = APIRouter(prefix="/api/equipos", tags=["equipos"])


@router.get("/mis-equipos", response_model=EquipoListResponse)
async def list_mis_equipos(
    materia_id: str | None = Query(default=None),
    rol: str | None = Query(default=None),
    estado_vigencia: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = EquipoService(current_user.tenant_id)
    result = await svc.listar_mis_equipos(
        db,
        usuario_id=current_user.id,
        materia_id=uuid.UUID(materia_id) if materia_id else None,
        rol=rol,
        estado_vigencia=estado_vigencia,
    )
    return EquipoListResponse(
        data=[EquipoItemResponse.model_validate(a) for a in result],
        total=len(result),
    )


@router.post(
    "/asignacion-masiva",
    response_model=AsignacionMasivaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def asignacion_masiva(
    body: AsignacionMasivaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = EquipoService(current_user.tenant_id)
    try:
        ids_creados = await svc.asignacion_masiva(db, body, current_user.id)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=422, detail="Invalid usuario_id or FK constraint violation"
        )
    return AsignacionMasivaResponse(ids_creados=ids_creados)


@router.post(
    "/clonar",
    response_model=ClonarResponse,
    status_code=status.HTTP_201_CREATED,
)
async def clonar_equipo(
    body: ClonarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = EquipoService(current_user.tenant_id)
    try:
        ids_creados = await svc.clonar_equipo(db, body, current_user.id)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=422, detail="FK constraint violation during clone"
        )

    if not ids_creados:
        return JSONResponse(
            content=ClonarResponse(ids_creados=[]).model_dump(mode="json"),
            status_code=200,
        )

    return ClonarResponse(ids_creados=ids_creados)


@router.patch("/{asignacion_id}/vigencia", response_model=EquipoItemResponse)
async def modificar_vigencia(
    asignacion_id: uuid.UUID,
    body: VigenciaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = EquipoService(current_user.tenant_id)
    try:
        asignacion = await svc.modificar_vigencia(
            db, asignacion_id, body, current_user.id
        )
        await db.commit()
        await db.refresh(asignacion)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Asignacion not found")
    return EquipoItemResponse.model_validate(asignacion)


@router.patch(
    "/vigencia-masiva",
    response_model=VigenciaMasivaResponse,
)
async def modificar_vigencia_masiva(
    body: VigenciaMasivaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = EquipoService(current_user.tenant_id)
    vig_req = VigenciaRequest(desde=body.desde, hasta=body.hasta)
    filas = await svc.modificar_vigencia_masiva(
        db, body.materia_id, body.cohorte_id, vig_req, current_user.id
    )
    await db.commit()
    return VigenciaMasivaResponse(filas_afectadas=filas)


@router.get("/{asignacion_id}/exportar")
async def exportar_equipo(
    asignacion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = EquipoService(current_user.tenant_id)
    try:
        xlsx_data = await svc.exportar_equipo(db, asignacion_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Asignacion not found")

    return Response(
        content=xlsx_data,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="equipo_{asignacion_id}.xlsx"'
            )
        },
    )
