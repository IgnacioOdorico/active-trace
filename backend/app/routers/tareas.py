import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.tarea import (
    ComentarioCreateRequest,
    ComentarioListResponse,
    TareaCreateRequest,
    TareaListResponse,
    TareaResponse,
    TareaUpdateRequest,
    UsuarioAsignableResponse,
)
from app.services.tarea_service import TareaService
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/tareas", tags=["tareas"])

_ROLES_ASIGNABLES = {"ADMIN", "COORDINADOR", "PROFESOR", "TUTOR", "NEXO", "FINANZAS"}


def _get_svc(current_user: User) -> TareaService:
    return TareaService(current_user.tenant_id)


@router.post("", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
async def crear_tarea(
    body: TareaCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    data = body.model_dump()
    result = await svc.crear(data, current_user.id, db)
    await db.commit()
    return result


@router.get("/mias", response_model=TareaListResponse)
async def listar_mis_tareas(
    estado: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    return await svc.listar_mias(
        usuario_id=current_user.id,
        estado=estado,
        pagina=pagina,
        page_size=page_size,
        db=db,
    )


@router.get("/asignables", response_model=list[UsuarioAsignableResponse])
async def listar_asignables(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = UsuarioService(current_user.tenant_id)
    users, _ = await svc.get_all(db, page=1, page_size=200, estado="Activo")
    return [
        {
            "id": str(u.id),
            "nombre": u.nombre,
            "apellidos": u.apellidos,
            "email": u.email,
        }
        for u in users
        if any(rol.codigo in _ROLES_ASIGNABLES for rol in u.roles)
    ]


@router.get("", response_model=TareaListResponse)
async def listar_todas_las_tareas(
    asignado_a: uuid.UUID | None = Query(None),
    asignado_por: uuid.UUID | None = Query(None),
    materia_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    busqueda: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    return await svc.listar_todas(
        asignado_a=asignado_a,
        asignado_por=asignado_por,
        materia_id=materia_id,
        estado=estado,
        busqueda=busqueda,
        pagina=pagina,
        page_size=page_size,
        db=db,
    )


@router.get("/{id}", response_model=TareaResponse)
async def obtener_tarea(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    result = await svc.obtener(id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    return result


@router.patch("/{id}", response_model=TareaResponse)
async def editar_tarea(
    id: uuid.UUID,
    body: TareaUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    try:
        result = await svc.editar(id, data, current_user.id, db)
        await db.commit()
        return result
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail,
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_tarea(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    try:
        await svc.eliminar(id, db)
        await db.commit()
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )


@router.get("/{id}/comentarios", response_model=ComentarioListResponse)
async def listar_comentarios_tarea(
    id: uuid.UUID,
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    return await svc.listar_comentarios(
        tarea_id=id,
        pagina=pagina,
        page_size=page_size,
        db=db,
    )


@router.post("/{id}/comentarios")
async def agregar_comentario_tarea(
    id: uuid.UUID,
    body: ComentarioCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    try:
        result = await svc.agregar_comentario(
            id, body.texto, current_user.id, db
        )
        await db.commit()
        return result
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail,
        )
