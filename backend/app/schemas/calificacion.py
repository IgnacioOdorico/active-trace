from pydantic import BaseModel


class ActividadDetectada(BaseModel):
    nombre: str
    tipo: str  # "numerica" | "textual"


class ImportPreviewResponse(BaseModel):
    actividades: list[ActividadDetectada]
    preview: list[dict]
    total_filas: int


class CalificacionResponse(BaseModel):
    id: str
    entrada_padron_id: str
    materia_id: str
    nombre_actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None
    aprobado: bool
    origen: str

    model_config = {"from_attributes": True}


class ImportRequest(BaseModel):
    materia_id: str
    actividad_ids: list[str]


class ImportResponse(BaseModel):
    insertadas: int
    actualizadas: int
    filas_afectadas: int
    errores: list[dict]
    advertencias: list[dict]


class ReporteFinalizacionResponse(BaseModel):
    entregas_sin_calificar: list[dict]
    total: int
