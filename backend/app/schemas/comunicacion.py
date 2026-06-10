from pydantic import BaseModel


class PreviewRequest(BaseModel):
    materia_id: str
    destinatario_email: str
    asunto_template: str
    cuerpo_template: str


class PreviewResponse(BaseModel):
    asunto: str
    cuerpo: str


class CrearComunicacionRequest(BaseModel):
    materia_id: str
    destinatarios: list[str]
    asunto_template: str
    cuerpo_template: str


class EstadoCount(BaseModel):
    estado: str
    cantidad: int


class LoteResponse(BaseModel):
    lote_id: str
    total: int
    conteo_por_estado: dict[str, int]
    primer_envio: str | None = None
    ultimo_envio: str | None = None


class AprobarLoteRequest(BaseModel):
    lote_id: str


class ComunicacionResponse(BaseModel):
    id: str
    tenant_id: str
    enviado_por: str
    materia_id: str
    destinatario: str
    asunto: str
    cuerpo: str
    lote_id: str | None = None
    intentos: int = 0
    error_msg: str | None = None
    estado: str
    enviado_at: str | None = None
    enqueue_at: str | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}


class ComunicacionListResponse(BaseModel):
    items: list[ComunicacionResponse]
    total: int
    pagina: int
    por_pagina: int
