import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.core.config import settings
from app.models.user import User
from app.repositories.factura import FacturaRepository
from app.services.audit_service import AuditLogService, FACTURA_ABONAR, FACTURA_CARGAR

import os
import math

router = APIRouter(prefix="/api/facturas", tags=["facturas"])

MAX_FILE_SIZE_KB = 10240


async def save_factura_pdf(
    tenant_id: uuid.UUID,
    usuario_id: uuid.UUID,
    periodo: str,
    file: UploadFile,
) -> tuple[str, float]:
    upload_dir = os.path.join(
        getattr(settings, "FACTURAS_DIR", "/data/facturas"),
        str(tenant_id),
        periodo,
    )
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "factura.pdf")[1].lower()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{usuario_id}_{timestamp}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    size_kb = math.ceil(len(content) / 1024)

    with open(filepath, "wb") as f:
        f.write(content)

    return filepath, float(size_kb)


@router.post("", status_code=status.HTTP_201_CREATED)
async def cargar_factura(
    periodo: str = Form(...),
    detalle: str = Form(...),
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("facturas:cargar")),
):
    ext = os.path.splitext(archivo.filename or "")[1].lower()
    if ext != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser PDF",
        )

    content = await archivo.read()
    size_kb = math.ceil(len(content) / 1024)
    if size_kb > MAX_FILE_SIZE_KB:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE_KB} KB",
        )

    upload_dir = os.path.join(
        getattr(settings, "FACTURAS_DIR", "/data/facturas"),
        str(current_user.tenant_id),
        periodo,
    )
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}.pdf"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    repo = FacturaRepository(current_user.tenant_id)
    data = {
        "usuario_id": current_user.id,
        "periodo": periodo,
        "detalle": detalle,
        "referencia_archivo": filepath,
        "tamano_kb": float(size_kb),
        "cargada_at": datetime.now(timezone.utc),
    }
    entity = await repo.create(db, data)
    await db.commit()

    audit = AuditLogService(current_user.tenant_id)
    await audit.log(
        db, actor_id=current_user.id, accion=FACTURA_CARGAR,
        detalle={
            "factura_id": str(entity.id),
            "periodo": periodo,
            "tamano_kb": size_kb,
        },
    )
    await db.commit()

    return {
        "id": str(entity.id),
        "periodo": entity.periodo,
        "detalle": entity.detalle,
        "referencia_archivo": entity.referencia_archivo,
        "tamano_kb": float(entity.tamano_kb),
        "estado": entity.estado,
    }


@router.get("", status_code=status.HTTP_200_OK)
async def listar_facturas(
    periodo: str | None = Query(None),
    estado: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("facturas:ver")),
):
    repo = FacturaRepository(current_user.tenant_id)
    items = await repo.listar_por_filtros(db, periodo=periodo, estado=estado)
    return [
        {
            "id": str(f.id),
            "usuario_id": str(f.usuario_id),
            "periodo": f.periodo,
            "detalle": f.detalle,
            "referencia_archivo": f.referencia_archivo,
            "tamano_kb": float(f.tamano_kb),
            "estado": f.estado,
            "cargada_at": str(f.cargada_at),
            "abonada_at": str(f.abonada_at) if f.abonada_at else None,
        }
        for f in items
    ]


@router.patch("/{id}/abonar", status_code=status.HTTP_200_OK)
async def abonar_factura(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("facturas:abonar")),
):
    repo = FacturaRepository(current_user.tenant_id)
    try:
        entity = await repo.abonar(db, id)
        await db.commit()
        audit = AuditLogService(current_user.tenant_id)
        await audit.log(
            db, actor_id=current_user.id, accion=FACTURA_ABONAR,
            detalle={"factura_id": str(id)},
        )
        await db.commit()
        return {
            "id": str(entity.id),
            "estado": entity.estado,
            "abonada_at": str(entity.abonada_at) if entity.abonada_at else None,
        }
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e.detail,
        )
