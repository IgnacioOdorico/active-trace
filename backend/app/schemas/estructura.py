from datetime import datetime

from pydantic import BaseModel


class CarreraCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None


class CarreraUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None


class CarreraResponse(BaseModel):
    id: str
    codigo: str
    nombre: str
    descripcion: str | None = None
    activa: bool
    created_at: datetime
    updated_at: datetime


class CohorteCreate(BaseModel):
    nombre: str
    carrera_id: str
    fecha_inicio: datetime
    fecha_fin: datetime


class CohorteUpdate(BaseModel):
    nombre: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None


class CohorteResponse(BaseModel):
    id: str
    nombre: str
    carrera_id: str
    fecha_inicio: datetime
    fecha_fin: datetime
    activa: bool
    created_at: datetime
    updated_at: datetime


class MateriaCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None
    carrera_id: str | None = None


class MateriaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    carrera_id: str | None = None


class MateriaResponse(BaseModel):
    id: str
    codigo: str
    nombre: str
    descripcion: str | None = None
    carrera_id: str | None = None
    created_at: datetime
    updated_at: datetime
