from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProgramaMateriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    materia_id: str
    carrera_id: str
    cohorte_id: str
    titulo: str
    referencia_archivo: str
    cargado_at: datetime
    created_at: datetime
    updated_at: datetime


class ProgramaMateriaCreateRequest(BaseModel):
    materia_id: str
    carrera_id: str
    cohorte_id: str
    titulo: str
    referencia_archivo: str


class ProgramaMateriaUpdateRequest(BaseModel):
    titulo: str | None = None
    referencia_archivo: str | None = None


class ProgramaMateriaListResponse(BaseModel):
    items: list[ProgramaMateriaResponse]
    total: int
