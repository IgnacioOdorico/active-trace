import uuid
from datetime import datetime

from pydantic import BaseModel


class FacturaResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: uuid.UUID
    periodo: str
    detalle: str
    referencia_archivo: str
    tamano_kb: float
    estado: str
    cargada_at: str
    abonada_at: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class FacturaAbonar(BaseModel):
    pass
