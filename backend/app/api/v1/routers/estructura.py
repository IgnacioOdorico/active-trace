import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError, EntityNotFoundError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.estructura import (
    CarreraCreate,
    CarreraResponse,
    CarreraUpdate,
    CohorteCreate,
    CohorteResponse,
    CohorteUpdate,
    MateriaCreate,
    MateriaResponse,
    MateriaUpdate,
)
from app.services.carrera_service import CarreraService
from app.services.cohorte_service import CohorteService
from app.services.materia_service import MateriaService

router = APIRouter(prefix="/api/v1/admin", tags=["estructura"])
router_public = APIRouter(prefix="/api/v1/estructura", tags=["estructura"])


def _carrera_to_response(c) -> CarreraResponse:
    return CarreraResponse(
        id=str(c.id),
        codigo=c.codigo,
        nombre=c.nombre,
        descripcion=c.descripcion,
        activa=c.activa,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _cohorte_to_response(c) -> CohorteResponse:
    return CohorteResponse(
        id=str(c.id),
        nombre=c.nombre,
        carrera_id=str(c.carrera_id),
        fecha_inicio=c.fecha_inicio,
        fecha_fin=c.fecha_fin,
        activa=c.activa,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _materia_to_response(m) -> MateriaResponse:
    return MateriaResponse(
        id=str(m.id),
        codigo=m.codigo,
        nombre=m.nombre,
        descripcion=m.descripcion,
        carrera_id=str(m.carrera_id) if m.carrera_id else None,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.get("/carreras", response_model=list[CarreraResponse])
async def list_carreras(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CarreraService(current_user.tenant_id)
    carreras = await svc.get_all(db)
    return [_carrera_to_response(c) for c in carreras]


@router.post("/carreras", response_model=CarreraResponse, status_code=status.HTTP_201_CREATED)
async def create_carrera(
    body: CarreraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CarreraService(current_user.tenant_id)
    try:
        carrera = await svc.create(db, body)
    except DomainError as e:
        raise HTTPException(status_code=409, detail=e.detail)
    await db.commit()
    return _carrera_to_response(carrera)


@router.get("/carreras/{carrera_id}", response_model=CarreraResponse)
async def get_carrera(
    carrera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CarreraService(current_user.tenant_id)
    try:
        carrera = await svc.get(db, carrera_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Carrera not found")
    return _carrera_to_response(carrera)


@router.put("/carreras/{carrera_id}", response_model=CarreraResponse)
async def update_carrera(
    carrera_id: uuid.UUID,
    body: CarreraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CarreraService(current_user.tenant_id)
    try:
        carrera = await svc.update(db, carrera_id, body)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Carrera not found")
    await db.commit()
    return _carrera_to_response(carrera)


@router.delete("/carreras/{carrera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carrera(
    carrera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CarreraService(current_user.tenant_id)
    await svc.soft_delete(db, carrera_id)
    await db.commit()


@router.get("/cohortes", response_model=list[CohorteResponse])
async def list_cohortes(
    carrera_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CohorteService(current_user.tenant_id)
    cohortes = await svc.get_all(db, carrera_id=carrera_id)
    return [_cohorte_to_response(c) for c in cohortes]


@router.post("/cohortes", response_model=CohorteResponse, status_code=status.HTTP_201_CREATED)
async def create_cohorte(
    body: CohorteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CohorteService(current_user.tenant_id)
    try:
        cohorte = await svc.create(db, body)
    except (DomainError, EntityNotFoundError) as e:
        raise HTTPException(status_code=409, detail=e.detail)
    await db.commit()
    return _cohorte_to_response(cohorte)


@router.get("/cohortes/{cohorte_id}", response_model=CohorteResponse)
async def get_cohorte(
    cohorte_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CohorteService(current_user.tenant_id)
    try:
        cohorte = await svc.get(db, cohorte_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Cohorte not found")
    return _cohorte_to_response(cohorte)


@router.put("/cohortes/{cohorte_id}", response_model=CohorteResponse)
async def update_cohorte(
    cohorte_id: uuid.UUID,
    body: CohorteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CohorteService(current_user.tenant_id)
    try:
        cohorte = await svc.update(db, cohorte_id, body)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Cohorte not found")
    await db.commit()
    return _cohorte_to_response(cohorte)


@router.delete("/cohortes/{cohorte_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cohorte(
    cohorte_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = CohorteService(current_user.tenant_id)
    await svc.soft_delete(db, cohorte_id)
    await db.commit()


@router.get("/materias", response_model=list[MateriaResponse])
async def list_materias(
    carrera_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = MateriaService(current_user.tenant_id)
    materias = await svc.get_all(db, carrera_id=carrera_id)
    return [_materia_to_response(m) for m in materias]


@router.post("/materias", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(
    body: MateriaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = MateriaService(current_user.tenant_id)
    try:
        materia = await svc.create(db, body)
    except DomainError as e:
        raise HTTPException(status_code=409, detail=e.detail)
    await db.commit()
    return _materia_to_response(materia)


@router.get("/materias/{materia_id}", response_model=MateriaResponse)
async def get_materia(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = MateriaService(current_user.tenant_id)
    try:
        materia = await svc.get(db, materia_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Materia not found")
    return _materia_to_response(materia)


@router.put("/materias/{materia_id}", response_model=MateriaResponse)
async def update_materia(
    materia_id: uuid.UUID,
    body: MateriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = MateriaService(current_user.tenant_id)
    try:
        materia = await svc.update(db, materia_id, body)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Materia not found")
    await db.commit()
    return _materia_to_response(materia)


@router.delete("/materias/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("estructura:gestionar")),
):
    svc = MateriaService(current_user.tenant_id)
    await svc.soft_delete(db, materia_id)
    await db.commit()


@router_public.get("/materias")
async def list_materias_public(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = MateriaService(current_user.tenant_id)
    materias = await svc.get_all(db)
    return [
        {"id": str(m.id), "nombre": m.nombre, "codigo": m.codigo, "comision": None, "regional": None}
        for m in materias
    ]
