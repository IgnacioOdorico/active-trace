from datetime import datetime

from pydantic import BaseModel


class ImportPreviewResponse(BaseModel):
    filas_detectadas: int
    columnas: list[str]
    preview: list[dict]


class VersionPadronResponse(BaseModel):
    id: str
    materia_id: str
    cohorte_id: str
    activa: bool
    cargado_por: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EntradaPadronResponse(BaseModel):
    id: str
    version_id: str
    usuario_id: str | None = None
    nombre: str
    apellidos: str
    email: str
    comision: str | None = None
    regional: str | None = None

    model_config = {"from_attributes": True}


class ConfirmImportResponse(BaseModel):
    version_id: str
    filas_creadas: int
    mensaje: str
