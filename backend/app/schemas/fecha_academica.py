from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class FechaAcademicaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    materia_id: str
    cohorte_id: str
    tipo: str
    numero: int
    periodo: str
    fecha: date
    titulo: str
    created_at: datetime
    updated_at: datetime


class FechaAcademicaCreateRequest(BaseModel):
    materia_id: str
    cohorte_id: str
    tipo: str
    numero: int
    periodo: str
    fecha: date
    titulo: str


class FechaAcademicaUpdateRequest(BaseModel):
    tipo: str | None = None
    numero: int | None = None
    periodo: str | None = None
    fecha: date | None = None
    titulo: str | None = None


class FechaAcademicaListResponse(BaseModel):
    items: list[FechaAcademicaResponse]
    total: int


class FragmentoLMSResponse(BaseModel):
    html: str
