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
)
from app.services.tarea_service import TareaService

router = APIRouter(prefix="/api/tareas", tags=["tareas"])


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
    if data.get("materia_id"):
        data["materia_id"] = uuid.UUID(data["materia_id"])
    data["asignado_a"] = uuid.UUID(data["asignado_a"])
    if data.get("contexto_id"):
        data["contexto_id"] = uuid.UUID(data["contexto_id"])
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


@router.get("", response_model=TareaListResponse)
async def listar_todas_las_tareas(
    asignado_a: str | None = Query(None),
    asignado_por: str | None = Query(None),
    materia_id: str | None = Query(None),
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
        asignado_a=uuid.UUID(asignado_a) if asignado_a else None,
        asignado_por=uuid.UUID(asignado_por) if asignado_por else None,
        materia_id=uuid.UUID(materia_id) if materia_id else None,
        estado=estado,
        busqueda=busqueda,
        pagina=pagina,
        page_size=page_size,
        db=db,
    )


@router.get("/{id}", response_model=TareaResponse)
async def obtener_tarea(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    result = await svc.obtener(uuid.UUID(id), db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    return result


@router.patch("/{id}", response_model=TareaResponse)
async def editar_tarea(
    id: str,
    body: TareaUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    if "asignado_a" in data:
        data["asignado_a"] = uuid.UUID(data["asignado_a"])
    try:
        result = await svc.editar(uuid.UUID(id), data, current_user.id, db)
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
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    try:
        await svc.eliminar(uuid.UUID(id), db)
        await db.commit()
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )


@router.get("/{id}/comentarios", response_model=ComentarioListResponse)
async def listar_comentarios_tarea(
    id: str,
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    return await svc.listar_comentarios(
        tarea_id=uuid.UUID(id),
        pagina=pagina,
        page_size=page_size,
        db=db,
    )


@router.post("/{id}/comentarios")
async def agregar_comentario_tarea(
    id: str,
    body: ComentarioCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tareas:gestionar")),
):
    svc = _get_svc(current_user)
    try:
        result = await svc.agregar_comentario(
            uuid.UUID(id), body.texto, current_user.id, db
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
