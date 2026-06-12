import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.coloquio import (
    CrearEvaluacionRequest,
    ImportarAlumnosRequest,
    ReservarTurnoRequest,
    RegistrarResultadoRequest,
    EvaluacionListResponse,
    EvaluacionDetailResponse,
    MetricasResponse,
    MetricasConvocatoriaResponse,
    AgendaResponse,
    ConvocatoriaDisponibleResponse,
    ReservaEvaluacionResponse,
    ResultadoEvaluacionResponse,
)
from app.services.coloquio_service import ColoquioService

router = APIRouter(prefix="/api/coloquios", tags=["coloquios"])


@router.get("/metricas", response_model=MetricasResponse)
async def obtener_metricas_globales(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    return await svc.obtener_metricas_globales(db)


@router.get("/disponibles", response_model=list[ConvocatoriaDisponibleResponse])
async def listar_disponibles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:reservar")),
):
    svc = ColoquioService(current_user.tenant_id)
    return await svc.listar_disponibles(current_user.id, db)


@router.get("/mis-reservas", response_model=list[ReservaEvaluacionResponse])
async def listar_mis_reservas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:reservar")),
):
    svc = ColoquioService(current_user.tenant_id)
    return await svc.listar_mis_reservas(current_user.id, db)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def crear_convocatoria(
    body: CrearEvaluacionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    try:
        result = await svc.crear_convocatoria(
            body.model_dump(), current_user.id, db
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("", response_model=EvaluacionListResponse)
async def listar_convocatorias(
    materia_id: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    filtros = {"materia_id": materia_id}
    return await svc.listar_convocatorias(
        filtros, pagina=pagina, page_size=page_size, db=db
    )


@router.get("/{id}", response_model=EvaluacionDetailResponse)
async def obtener_evaluacion(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    evaluacion = await svc._evaluacion_repo.get(db, uuid.UUID(id))
    if evaluacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada",
        )
    return evaluacion


@router.patch("/{id}", response_model=dict)
async def editar_convocatoria(
    id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    try:
        result = await svc.editar_convocatoria(
            uuid.UUID(id), body, db
        )
        await db.commit()
        return result
    except DomainError as e:
        if "cerrada" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail,
            )
        if "no encontrada" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.detail,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.patch("/{id}/cerrar", response_model=dict)
async def cerrar_convocatoria(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    try:
        result = await svc.cerrar_convocatoria(
            uuid.UUID(id), current_user.id, db
        )
        await db.commit()
        return result
    except DomainError as e:
        if "ya está cerrada" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail,
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.post("/{id}/alumnos", response_model=dict)
async def importar_alumnos(
    id: str,
    body: ImportarAlumnosRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    try:
        cantidad = await svc.importar_alumnos(
            uuid.UUID(id), body.alumno_ids, db
        )
        await db.commit()
        return {"cantidad_importados": cantidad}
    except DomainError as e:
        if "no encontrada" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.detail,
            )
        if "no encontrados" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.detail,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.post("/{id}/reservar", response_model=dict, status_code=status.HTTP_201_CREATED)
async def reservar_turno(
    id: str,
    body: ReservarTurnoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:reservar")),
):
    svc = ColoquioService(current_user.tenant_id)
    try:
        result = await svc.reservar_turno(
            uuid.UUID(id), uuid.UUID(body.evaluacion_dia_id), current_user.id, db
        )
        await db.commit()
        return result
    except DomainError as e:
        if "Cupo agotado" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=e.detail,
            )
        if "No está habilitado" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.detail,
            )
        if "no encontrada" in e.detail or "no encontrado" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.detail,
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.patch("/reservas/{reserva_id}/cancelar", response_model=dict)
async def cancelar_reserva(
    reserva_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:reservar")),
):
    svc = ColoquioService(current_user.tenant_id)
    try:
        result = await svc.cancelar_reserva(
            uuid.UUID(reserva_id), current_user.id, db
        )
        await db.commit()
        return result
    except DomainError as e:
        if "ya está cancelada" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail,
            )
        if "de otro alumno" in e.detail:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.detail,
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.post("/{id}/resultados", response_model=dict)
async def registrar_resultado(
    id: str,
    body: RegistrarResultadoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    try:
        result = await svc.registrar_resultado(
            uuid.UUID(id), uuid.UUID(body.alumno_id), body.nota_final, db
        )
        await db.commit()
        return result
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail,
        )


@router.get("/{id}/resultados", response_model=list[ResultadoEvaluacionResponse])
async def listar_resultados(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    return await svc.listar_resultados(uuid.UUID(id), db)


@router.get("/{id}/metricas", response_model=MetricasConvocatoriaResponse)
async def obtener_metricas_convocatoria(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    return await svc.obtener_metricas_convocatoria(uuid.UUID(id), db)


@router.get("/{id}/agenda", response_model=list[AgendaResponse])
async def obtener_agenda(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("coloquios:gestionar")),
):
    svc = ColoquioService(current_user.tenant_id)
    return await svc.obtener_agenda(uuid.UUID(id), db)
