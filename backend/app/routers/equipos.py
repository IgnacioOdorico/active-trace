import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.core.permissions import require_permission
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.user import User
from app.schemas.equipos import (
    AsignacionMasivaRequest,
    AsignacionMasivaResponse,
    ClonarRequest,
    ClonarResponse,
    DocenteDisponibleResponse,
    EquipoItemResponse,
    EquipoListResponse,
    VigenciaMasivaRequest,
    VigenciaMasivaResponse,
    VigenciaRequest,
)
from app.services.equipo_service import EquipoService

router = APIRouter(prefix="/api/equipos", tags=["equipos"])


async def _enriquecer_asignaciones(
    db: AsyncSession, asignaciones: list
) -> list[EquipoItemResponse]:
    """Batch-load related entities to enrich the response with human-readable names."""
    materia_ids = {a.materia_id for a in asignaciones if a.materia_id}
    cohorte_ids = {a.cohorte_id for a in asignaciones if a.cohorte_id}

    materias_map: dict[uuid.UUID, Materia] = {}
    if materia_ids:
        res = await db.execute(
            select(Materia).where(Materia.id.in_(materia_ids), Materia.deleted_at.is_(None))
        )
        materias_map = {m.id: m for m in res.scalars()}

    all_carrera_ids = {a.carrera_id for a in asignaciones if a.carrera_id} | {
        m.carrera_id for m in materias_map.values() if m.carrera_id
    }
    carreras_map: dict[uuid.UUID, Carrera] = {}
    if all_carrera_ids:
        res = await db.execute(
            select(Carrera).where(Carrera.id.in_(all_carrera_ids), Carrera.deleted_at.is_(None))
        )
        carreras_map = {c.id: c for c in res.scalars()}

    cohortes_map: dict[uuid.UUID, Cohorte] = {}
    if cohorte_ids:
        res = await db.execute(
            select(Cohorte).where(Cohorte.id.in_(cohorte_ids), Cohorte.deleted_at.is_(None))
        )
        cohortes_map = {c.id: c for c in res.scalars()}

    items = []
    for a in asignaciones:
        materia = materias_map.get(a.materia_id) if a.materia_id else None
        carrera_id = a.carrera_id or (materia.carrera_id if materia else None)
        carrera = carreras_map.get(carrera_id) if carrera_id else None
        cohorte = cohortes_map.get(a.cohorte_id) if a.cohorte_id else None
        items.append(EquipoItemResponse(
            id=a.id,
            tenant_id=a.tenant_id,
            usuario_id=a.usuario_id,
            rol=a.rol,
            materia_id=a.materia_id,
            materia_nombre=materia.nombre if materia else None,
            carrera_id=carrera_id,
            carrera=carrera.nombre if carrera else None,
            cohorte_id=a.cohorte_id,
            cohorte=cohorte.nombre if cohorte else None,
            comisiones=a.comisiones,
            responsable_id=a.responsable_id,
            desde=a.desde,
            hasta=a.hasta,
            vigencia_desde=a.desde.strftime("%Y-%m-%d") if a.desde else "",
            vigencia_hasta=a.hasta.strftime("%Y-%m-%d") if a.hasta else "–",
            activo=a.estado_vigencia == "Vigente",
            estado_vigencia=a.estado_vigencia,
            created_at=a.created_at,
            updated_at=a.updated_at,
        ))

    return items


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
    asignaciones = await svc.listar_mis_equipos(
        db,
        usuario_id=current_user.id,
        materia_id=uuid.UUID(materia_id) if materia_id else None,
        rol=rol,
        estado_vigencia=estado_vigencia,
    )

    items = await _enriquecer_asignaciones(db, asignaciones)

    return EquipoListResponse(data=items, total=len(items))


@router.get("/docentes-disponibles", response_model=list[DocenteDisponibleResponse])
async def docentes_disponibles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("equipos:asignar")),
):
    svc = EquipoService(current_user.tenant_id)
    return await svc.listar_docentes_disponibles(db)


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
    items = await _enriquecer_asignaciones(db, [asignacion])
    return items[0]


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
