from datetime import datetime

from pydantic import BaseModel


class PerfilResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    nombre: str | None = None
    apellidos: str | None = None
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool
    estado: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PerfilUpdate(BaseModel):
    nombre: str | None = None
    apellidos: str | None = None
    dni: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    email: str | None = None
    legajo_profesional: str | None = None
    facturador: bool | None = None

    model_config = {"extra": "forbid"}
