import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.analisis import (
    AlumnoAtrasadoResponse,
    MonitorPaginationResponse,
    NotaFinalItemResponse,
    NotasFinalesRequest,
    RankingItemResponse,
    ReportesResponse,
)
from app.services.analisis_service import AnalisisService

router = APIRouter(prefix="/api/analisis", tags=["analisis"])


@router.get(
    "/atrasados/{materia_id}",
    response_model=list[AlumnoAtrasadoResponse],
)
async def atrasados(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("atrasados:ver")),
):
    svc = AnalisisService(current_user.tenant_id)
    try:
        return await svc.atrasados(db, materia_id)
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get(
    "/ranking/{materia_id}",
    response_model=list[RankingItemResponse],
)
async def ranking(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("atrasados:ver")),
):
    svc = AnalisisService(current_user.tenant_id)
    return await svc.ranking(db, materia_id)


@router.get(
    "/reportes/{materia_id}",
    response_model=ReportesResponse,
)
async def reportes(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("atrasados:ver")),
):
    svc = AnalisisService(current_user.tenant_id)
    return await svc.reportes_rapidos(db, materia_id)


@router.post(
    "/notas-finales",
    response_model=list[NotaFinalItemResponse],
)
async def notas_finales(
    body: NotasFinalesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("atrasados:ver")),
):
    svc = AnalisisService(current_user.tenant_id)
    try:
        actividades = [(a, "numerica") for a in body.actividades]
        return await svc.notas_finales(db, body.materia_id, actividades)
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("/exportar-tps/{materia_id}")
async def exportar_tps(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("atrasados:ver")),
):
    svc = AnalisisService(current_user.tenant_id)
    result = await svc.exportar_tps(db, materia_id)

    if "content" in result:
        return Response(
            content=result["content"],
            media_type=result["content_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{result["filename"]}"'
            },
        )

    return {
        "total": result.get("total", 0),
        "mensaje": result.get("mensaje", ""),
    }


@router.get(
    "/monitor-general",
    response_model=MonitorPaginationResponse,
)
async def monitor_general(
    materia_id: uuid.UUID | None = Query(default=None),
    regional: str | None = Query(default=None),
    comision: str | None = Query(default=None),
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("atrasados:ver")),
):
    svc = AnalisisService(current_user.tenant_id)
    return await svc.monitor_general(
        db,
        materia_id=materia_id,
        regional=regional,
        comision=comision,
        q=q,
        estado=estado,
        pagina=pagina,
        por_pagina=por_pagina,
    )


@router.get(
    "/monitor-seguimiento",
    response_model=MonitorPaginationResponse,
)
async def monitor_seguimiento(
    comision: str | None = Query(default=None),
    entrada_padron_id: uuid.UUID | None = Query(default=None),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("atrasados:ver")),
):
    svc = AnalisisService(current_user.tenant_id)

    desde_dt: datetime | None = None
    hasta_dt: datetime | None = None
    if desde is not None:
        desde_dt = datetime.combine(desde, datetime.min.time())
    if hasta is not None:
        hasta_dt = datetime.combine(hasta, datetime.max.time())

    return await svc.monitor_seguimiento(
        db,
        materias_ids=None,
        comision=comision,
        entrada_padron_id=entrada_padron_id,
        desde=desde_dt,
        hasta=hasta_dt,
        pagina=pagina,
        por_pagina=por_pagina,
    )
