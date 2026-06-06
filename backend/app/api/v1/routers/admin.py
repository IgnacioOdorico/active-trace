import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.permissions import require_permission
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.schemas.admin import (
    PermisoCreate,
    PermisoResponse,
    RolCreate,
    RolPermisoAssign,
    RolPermisoResponse,
    RolResponse,
    RolUpdate,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/roles", response_model=list[RolResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:roles")),
):
    result = await db.execute(select(Rol).where(Rol.activo == True).order_by(Rol.codigo))
    roles = result.scalars().all()
    return [
        RolResponse(
            id=str(r.id),
            codigo=r.codigo,
            nombre=r.nombre,
            descripcion=r.descripcion,
            activo=r.activo,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in roles
    ]


@router.post("/roles", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RolCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:roles")),
):
    existing = await db.execute(select(Rol).where(Rol.codigo == body.codigo))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Role codigo already exists")

    rol = Rol(codigo=body.codigo, nombre=body.nombre, descripcion=body.descripcion)
    db.add(rol)
    await db.commit()
    await db.refresh(rol)

    return RolResponse(
        id=str(rol.id),
        codigo=rol.codigo,
        nombre=rol.nombre,
        descripcion=rol.descripcion,
        activo=rol.activo,
        created_at=rol.created_at,
        updated_at=rol.updated_at,
    )


@router.put("/roles/{rol_id}", response_model=RolResponse)
async def update_role(
    rol_id: uuid.UUID,
    body: RolUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:roles")),
):
    result = await db.execute(select(Rol).where(Rol.id == rol_id, Rol.activo == True))
    rol = result.scalar_one_or_none()
    if rol is None:
        raise HTTPException(status_code=404, detail="Role not found")

    if body.nombre is not None:
        rol.nombre = body.nombre
    if body.descripcion is not None:
        rol.descripcion = body.descripcion

    await db.commit()
    await db.refresh(rol)

    return RolResponse(
        id=str(rol.id),
        codigo=rol.codigo,
        nombre=rol.nombre,
        descripcion=rol.descripcion,
        activo=rol.activo,
        created_at=rol.created_at,
        updated_at=rol.updated_at,
    )


@router.delete("/roles/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    rol_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:roles")),
):
    result = await db.execute(select(Rol).where(Rol.id == rol_id, Rol.activo == True))
    rol = result.scalar_one_or_none()
    if rol is None:
        raise HTTPException(status_code=404, detail="Role not found")

    rol.activo = False
    await db.commit()


@router.get("/permisos", response_model=list[PermisoResponse])
async def list_permisos(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:permisos")),
):
    result = await db.execute(select(Permiso).order_by(Permiso.codigo))
    permisos = result.scalars().all()
    return [
        PermisoResponse(
            id=str(p.id),
            codigo=p.codigo,
            nombre=p.nombre,
            descripcion=p.descripcion,
            modulo=p.modulo,
            propio=p.propio,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in permisos
    ]


@router.post("/permisos", response_model=PermisoResponse, status_code=status.HTTP_201_CREATED)
async def create_permiso(
    body: PermisoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:permisos")),
):
    existing = await db.execute(select(Permiso).where(Permiso.codigo == body.codigo))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Permission codigo already exists")

    modulo = body.codigo.split(":", 1)[0]
    permiso = Permiso(
        codigo=body.codigo,
        nombre=body.nombre,
        descripcion=body.descripcion,
        modulo=modulo,
        propio=body.propio,
    )
    db.add(permiso)
    await db.commit()
    await db.refresh(permiso)

    return PermisoResponse(
        id=str(permiso.id),
        codigo=permiso.codigo,
        nombre=permiso.nombre,
        descripcion=permiso.descripcion,
        modulo=permiso.modulo,
        propio=permiso.propio,
        created_at=permiso.created_at,
        updated_at=permiso.updated_at,
    )


@router.get("/roles/{rol_id}/permisos", response_model=list[PermisoResponse])
async def list_role_permisos(
    rol_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:roles")),
):
    result = await db.execute(select(Rol).where(Rol.id == rol_id, Rol.activo == True))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Role not found")

    result = await db.execute(
        select(Permiso)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .where(RolPermiso.rol_id == rol_id)
        .order_by(Permiso.codigo)
    )
    permisos = result.scalars().all()
    return [
        PermisoResponse(
            id=str(p.id),
            codigo=p.codigo,
            nombre=p.nombre,
            descripcion=p.descripcion,
            modulo=p.modulo,
            propio=p.propio,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in permisos
    ]


@router.post("/roles/{rol_id}/permisos", response_model=RolPermisoResponse, status_code=status.HTTP_201_CREATED)
async def assign_permiso(
    rol_id: uuid.UUID,
    body: RolPermisoAssign,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:roles")),
):
    rol = await db.get(Rol, rol_id)
    if rol is None or not rol.activo:
        raise HTTPException(status_code=404, detail="Role not found")

    permiso = await db.get(Permiso, uuid.UUID(body.permiso_id))
    if permiso is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    existing = await db.execute(
        select(RolPermiso).where(
            RolPermiso.rol_id == rol_id,
            RolPermiso.permiso_id == uuid.UUID(body.permiso_id),
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Permission already assigned to this role")

    rp = RolPermiso(rol_id=rol_id, permiso_id=uuid.UUID(body.permiso_id))
    db.add(rp)
    await db.commit()
    await db.refresh(rp)

    return RolPermisoResponse(
        id=str(rp.id),
        rol_id=str(rp.rol_id),
        permiso_id=str(rp.permiso_id),
    )


@router.delete("/roles/{rol_id}/permisos/{permiso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permiso(
    rol_id: uuid.UUID,
    permiso_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("admin:roles")),
):
    result = await db.execute(
        select(RolPermiso).where(
            RolPermiso.rol_id == rol_id,
            RolPermiso.permiso_id == permiso_id,
        )
    )
    rp = result.scalar_one_or_none()
    if rp is None:
        raise HTTPException(status_code=404, detail="Role-permission assignment not found")

    await db.delete(rp)
    await db.commit()
