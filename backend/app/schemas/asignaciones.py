from datetime import datetime

from pydantic import BaseModel


class AsignacionCreate(BaseModel):
    usuario_id: str
    rol: str
    materia_id: str | None = None
    carrera_id: str | None = None
    cohorte_id: str | None = None
    comisiones: list[str] | None = None
    responsable_id: str | None = None
    desde: datetime
    hasta: datetime | None = None


class AsignacionUpdate(BaseModel):
    rol: str | None = None
    materia_id: str | None = None
    carrera_id: str | None = None
    cohorte_id: str | None = None
    comisiones: list[str] | None = None
    responsable_id: str | None = None
    desde: datetime | None = None
    hasta: datetime | None = None


class AsignacionResponse(BaseModel):
    id: str
    tenant_id: str
    usuario_id: str
    rol: str
    materia_id: str | None = None
    carrera_id: str | None = None
    cohorte_id: str | None = None
    comisiones: list[str] | None = None
    responsable_id: str | None = None
    desde: datetime
    hasta: datetime | None = None
    estado_vigencia: str = "Vigente"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AsignacionList(BaseModel):
    data: list[AsignacionResponse]
    total: int
    page: int
    page_size: int
