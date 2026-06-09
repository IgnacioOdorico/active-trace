from pydantic import BaseModel


class UmbralConfigRequest(BaseModel):
    umbral_pct: float = 60.0
    valores_aprobatorios: list[str] | None = None


class UmbralMateriaResponse(BaseModel):
    id: str
    asignacion_id: str
    materia_id: str
    umbral_pct: float
    valores_aprobatorios: list[str] | None = None
    recalculo_aprobados: int

    model_config = {"from_attributes": True}
