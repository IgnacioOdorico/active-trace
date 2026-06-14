from pydantic import BaseModel, ConfigDict


class GuardiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    asignacion_id: str
    materia_id: str
    carrera_id: str
    cohorte_id: str | None = None
    dia: str
    horario: str
    estado: str
    comentarios: str | None = None


class GuardiaListResponse(BaseModel):
    items: list[GuardiaResponse]
    total: int
    pagina: int
    page_size: int


class CrearGuardiaRequest(BaseModel):
    materia_id: str
    carrera_id: str
    cohorte_id: str | None = None
    dia: str
    horario: str
    comentarios: str | None = None


class EditarGuardiaRequest(BaseModel):
    estado: str
    comentarios: str | None = None


class ExportGuardiasResponse(BaseModel):
    items: list[GuardiaResponse]
