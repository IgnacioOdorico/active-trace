import uuid
from datetime import date, datetime

from pydantic import BaseModel


class SalarioPlusCreate(BaseModel):
    grupo: str
    rol: str
    descripcion: str | None = None
    monto: float
    desde: date
    hasta: date | None = None


class SalarioPlusUpdate(BaseModel):
    grupo: str | None = None
    rol: str | None = None
    descripcion: str | None = None
    monto: float | None = None
    desde: date | None = None
    hasta: date | None = None


class SalarioPlusResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    grupo: str
    rol: str
    descripcion: str | None
    monto: float
    desde: date
    hasta: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
