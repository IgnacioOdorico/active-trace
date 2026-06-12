from datetime import datetime

from pydantic import BaseModel


class AvisoResponse(BaseModel):
    id: str
    tenant_id: str
    alcance: str
    materia_id: str | None = None
    cohorte_id: str | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: str
    fin_en: str
    orden: int
    activo: bool
    requiere_ack: bool
    created_at: str | None = None
    updated_at: str | None = None
    total_acks: int = 0

    model_config = {"from_attributes": True}


class AvisoCreateRequest(BaseModel):
    alcance: str
    materia_id: str | None = None
    cohorte_id: str | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int
    activo: bool = True
    requiere_ack: bool = False


class AvisoUpdateRequest(BaseModel):
    alcance: str | None = None
    materia_id: str | None = None
    cohorte_id: str | None = None
    rol_destino: str | None = None
    severidad: str | None = None
    titulo: str | None = None
    cuerpo: str | None = None
    inicio_en: datetime | None = None
    fin_en: datetime | None = None
    orden: int | None = None
    activo: bool | None = None
    requiere_ack: bool | None = None


class AvisoListResponse(BaseModel):
    items: list[AvisoResponse]
    total: int
    pagina: int
    page_size: int


class AcknowledgmentResponse(BaseModel):
    id: str
    aviso_id: str
    usuario_id: str
    confirmado_at: str

    model_config = {"from_attributes": True}


class ContadorResponse(BaseModel):
    total_acks: int
