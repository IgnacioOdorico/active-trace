import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.liquidacion import CalcularLiquidacionRequest, LiquidacionKPI, LiquidacionResponse
from app.services.audit_service import (
    AuditLogService,
    LIQUIDACION_CALCULAR,
    LIQUIDACION_CERRAR,
    LIQUIDACION_EXPORTAR,
)
from app.services.liquidaciones import LiquidacionService

router = APIRouter(prefix="/api/liquidaciones", tags=["liquidaciones"])


@router.post("/calcular", status_code=status.HTTP_200_OK)
async def calcular_liquidacion(
    body: CalcularLiquidacionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:calcular")),
):
    svc = LiquidacionService(current_user.tenant_id)
    try:
        result = await svc.calcular(db, body.cohorte_id, body.periodo)
        await db.commit()
        audit = AuditLogService(current_user.tenant_id)
        await audit.log(
            db, actor_id=current_user.id, accion=LIQUIDACION_CALCULAR,
            detalle={
                "cohorte_id": str(body.cohorte_id),
                "periodo": body.periodo,
                "cantidad": len(result),
            },
            filas_afectadas=len(result),
        )
        await db.commit()
        return {"liquidaciones": result, "total": len(result)}
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e.detail,
        )


@router.get("", status_code=status.HTTP_200_OK)
async def listar_liquidaciones(
    periodo: str = Query(...),
    cohorte_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:ver")),
):
    svc = LiquidacionService(current_user.tenant_id)
    items = await svc.listar(db, periodo, cohorte_id)
    return {"items": items, "total": len(items)}


@router.get("/historial", status_code=status.HTTP_200_OK)
async def historial_liquidaciones(
    cohorte_id: uuid.UUID | None = Query(None),
    desde: str | None = Query(None),
    hasta: str | None = Query(None),
    estado: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:ver")),
):
    svc = LiquidacionService(current_user.tenant_id)
    items = await svc.listar(db, hasta or "2099-12")
    result = []
    for item in items:
        if desde and item["periodo"] < desde:
            continue
        if estado and item["estado"] != estado:
            continue
        result.append(item)
    result.sort(key=lambda x: x["periodo"], reverse=True)
    return {"items": result, "total": len(result)}


@router.get("/kpis", response_model=LiquidacionKPI, status_code=status.HTTP_200_OK)
async def kpis_liquidaciones(
    periodo: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:ver")),
):
    svc = LiquidacionService(current_user.tenant_id)
    return await svc.obtener_kpis(db, periodo)


@router.get("/exportar", status_code=status.HTTP_200_OK)
async def exportar_planilla(
    periodo: str = Query(...),
    cohorte_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:exportar")),
):
    svc = LiquidacionService(current_user.tenant_id)
    xlsx_data = await svc.exportar_planilla(db, periodo, cohorte_id)

    audit = AuditLogService(current_user.tenant_id)
    await audit.log(
        db, actor_id=current_user.id, accion=LIQUIDACION_EXPORTAR,
        detalle={
            "periodo": periodo,
            "cohorte_id": str(cohorte_id) if cohorte_id else None,
        },
    )
    await db.commit()

    return Response(
        content=xlsx_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="liquidaciones_{periodo}.xlsx"'
        },
    )


@router.post("/{id}/cerrar", status_code=status.HTTP_200_OK)
async def cerrar_liquidacion(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:cerrar")),
):
    svc = LiquidacionService(current_user.tenant_id)
    try:
        result = await svc.cerrar(db, id)
        await db.commit()
        audit = AuditLogService(current_user.tenant_id)
        await audit.log(
            db, actor_id=current_user.id, accion=LIQUIDACION_CERRAR,
            detalle={"liquidacion_id": str(id)},
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e.detail,
        )
