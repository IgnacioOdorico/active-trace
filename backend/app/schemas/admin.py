from datetime import datetime

from pydantic import BaseModel


class RolCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None


class RolUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None


class RolResponse(BaseModel):
    id: str
    codigo: str
    nombre: str
    descripcion: str | None = None
    activo: bool
    created_at: datetime
    updated_at: datetime


class PermisoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None
    propio: bool = False


class PermisoResponse(BaseModel):
    id: str
    codigo: str
    nombre: str
    descripcion: str | None = None
    modulo: str
    propio: bool
    created_at: datetime
    updated_at: datetime


class RolPermisoAssign(BaseModel):
    permiso_id: str


class RolPermisoResponse(BaseModel):
    id: str
    rol_id: str
    permiso_id: str
