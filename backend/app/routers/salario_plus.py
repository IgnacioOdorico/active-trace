import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.permissions import require_permission
from app.models.user import User
from app.repositories.salario_plus import SalarioPlusRepository
from app.schemas.salario_plus import SalarioPlusCreate, SalarioPlusResponse, SalarioPlusUpdate
from app.services.audit_service import AuditLogService, SALARIO_CONFIGURAR

router = APIRouter(prefix="/api/salario-plus", tags=["salario-plus"])


@router.post("", response_model=SalarioPlusResponse, status_code=status.HTTP_201_CREATED)
async def crear_salario_plus(
    body: SalarioPlusCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:configurar-salarios")),
):
    repo = SalarioPlusRepository(current_user.tenant_id)
    try:
        entity = await repo.create(db, body.model_dump())
        await db.commit()
        audit = AuditLogService(current_user.tenant_id)
        await audit.log(
            db, actor_id=current_user.id, accion=SALARIO_CONFIGURAR,
            detalle={"tipo": "salario_plus", "accion": "crear", "id": str(entity.id)},
        )
        await db.commit()
        return entity
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e.detail,
        )


@router.get("", response_model=list[SalarioPlusResponse])
async def listar_salarios_plus(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:configurar-salarios")),
):
    repo = SalarioPlusRepository(current_user.tenant_id)
    return await repo.get_all(db)


@router.get("/{id}", response_model=SalarioPlusResponse)
async def obtener_salario_plus(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:configurar-salarios")),
):
    repo = SalarioPlusRepository(current_user.tenant_id)
    entity = await repo.get(db, id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salario plus no encontrado")
    return entity


@router.put("/{id}", response_model=SalarioPlusResponse)
async def actualizar_salario_plus(
    id: uuid.UUID,
    body: SalarioPlusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:configurar-salarios")),
):
    repo = SalarioPlusRepository(current_user.tenant_id)
    try:
        entity = await repo.update(db, id, body.model_dump(exclude_none=True))
        await db.commit()
        audit = AuditLogService(current_user.tenant_id)
        await audit.log(
            db, actor_id=current_user.id, accion=SALARIO_CONFIGURAR,
            detalle={"tipo": "salario_plus", "accion": "actualizar", "id": str(id)},
        )
        await db.commit()
        return entity
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e.detail,
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_salario_plus(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("liquidaciones:configurar-salarios")),
):
    repo = SalarioPlusRepository(current_user.tenant_id)
    entity = await repo.get(db, id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salario plus no encontrado")
    await repo.soft_delete(db, id)
    await db.commit()
    audit = AuditLogService(current_user.tenant_id)
    await audit.log(
        db, actor_id=current_user.id, accion=SALARIO_CONFIGURAR,
        detalle={"tipo": "salario_plus", "accion": "eliminar", "id": str(id)},
    )
    await db.commit()
