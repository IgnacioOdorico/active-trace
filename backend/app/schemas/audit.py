from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    fecha_hora: datetime
    actor_id: str
    impersonado_id: str | None = None
    materia_id: str | None = None
    accion: str
    detalle: dict | None = None
    filas_afectadas: int
    ip: str | None = None
    user_agent: str | None = None


class AuditLogFilter(BaseModel):
    actor_id: str | None = None
    materia_id: str | None = None
    accion: str | None = None
    desde: datetime | None = None
    hasta: datetime | None = None
    pagina: int = 1
    por_pagina: int = 50


class PaginatedAuditLogResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int


class ImpersonationStartRequest(BaseModel):
    target_user_id: str


class ImpersonationResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    impersonating: bool = True
