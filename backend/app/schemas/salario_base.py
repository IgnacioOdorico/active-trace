import uuid
from datetime import date

from pydantic import BaseModel


class SalarioBaseCreate(BaseModel):
    rol: str
    monto: float
    desde: date
    hasta: date | None = None


class SalarioBaseUpdate(BaseModel):
    rol: str | None = None
    monto: float | None = None
    desde: date | None = None
    hasta: date | None = None


class SalarioBaseResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    rol: str
    monto: float
    desde: date
    hasta: date | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
