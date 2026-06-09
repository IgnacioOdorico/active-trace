from datetime import datetime

from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    nombre: str | None = None
    apellidos: str | None = None
    email: str
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool = False
    estado: str = "Activo"
    password: str | None = None


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    apellidos: str | None = None
    email: str | None = None
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool | None = None
    estado: str | None = None
    password: str | None = None


class UsuarioResponse(BaseModel):
    id: str
    tenant_id: str
    nombre: str | None = None
    apellidos: str | None = None
    email: str
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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UsuarioList(BaseModel):
    data: list[UsuarioResponse]
    total: int
    page: int
    page_size: int
