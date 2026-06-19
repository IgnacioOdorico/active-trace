import uuid
from datetime import datetime

from pydantic import BaseModel


class AsignacionMasivaRequest(BaseModel):
    usuario_ids: list[uuid.UUID]
    rol: str
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    comisiones: list[str] | None = None
    desde: datetime
    hasta: datetime | None = None


class AsignacionMasivaResponse(BaseModel):
    ids_creados: list[uuid.UUID]


class DocenteDisponibleResponse(BaseModel):
    id: uuid.UUID
    nombre_completo: str
    email: str
    roles: list[str]


class ClonarRequest(BaseModel):
    materia_id: uuid.UUID
    cohorte_origen_id: uuid.UUID
    cohorte_destino_id: uuid.UUID
    desde: datetime
    hasta: datetime | None = None


class ClonarResponse(BaseModel):
    ids_creados: list[uuid.UUID]


class VigenciaRequest(BaseModel):
    desde: datetime | None = None
    hasta: datetime | None = None


class VigenciaMasivaRequest(BaseModel):
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    desde: datetime | None = None
    hasta: datetime | None = None


class EquipoItemResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: uuid.UUID
    rol: str
    materia_id: uuid.UUID | None = None
    materia_nombre: str | None = None
    carrera_id: uuid.UUID | None = None
    carrera: str | None = None
    cohorte_id: uuid.UUID | None = None
    cohorte: str | None = None
    comisiones: list[str] | None = None
    responsable_id: uuid.UUID | None = None
    desde: datetime
    hasta: datetime | None = None
    vigencia_desde: str = ""
    vigencia_hasta: str = "–"
    activo: bool = True
    estado_vigencia: str = "Vigente"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EquipoListResponse(BaseModel):
    data: list[EquipoItemResponse]
    total: int


class VigenciaMasivaResponse(BaseModel):
    filas_afectadas: int


class EquipoExportResponse(BaseModel):
    message: str = "OK"
