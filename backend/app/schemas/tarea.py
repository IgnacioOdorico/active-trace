from pydantic import BaseModel


class TareaResponse(BaseModel):
    id: str
    tenant_id: str
    materia_id: str | None = None
    asignado_a: str
    asignado_por: str
    estado: str
    descripcion: str
    contexto_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}


class TareaCreateRequest(BaseModel):
    asignado_a: str
    materia_id: str | None = None
    descripcion: str
    contexto_id: str | None = None


class TareaUpdateRequest(BaseModel):
    asignado_a: str | None = None
    descripcion: str | None = None
    estado: str | None = None


class TareaListResponse(BaseModel):
    items: list[TareaResponse]
    total: int
    pagina: int
    page_size: int


class ComentarioResponse(BaseModel):
    id: str
    tarea_id: str
    autor_id: str
    texto: str
    creado_at: str | None = None

    model_config = {"from_attributes": True}


class ComentarioCreateRequest(BaseModel):
    texto: str


class ComentarioListResponse(BaseModel):
    items: list[ComentarioResponse]
    total: int
    pagina: int
    page_size: int
