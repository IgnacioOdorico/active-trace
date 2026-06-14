from datetime import date, time

from pydantic import BaseModel, ConfigDict


class SlotEncuentroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    asignacion_id: str
    materia_id: str
    titulo: str
    hora: time
    dia_semana: str
    fecha_inicio: date
    cant_semanas: int
    fecha_unica: date | None = None
    meet_url: str
    vig_desde: date
    vig_hasta: date | None = None


class InstanciaEncuentroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slot_id: str | None = None
    materia_id: str
    fecha: date
    hora: time
    titulo: str
    estado: str
    meet_url: str
    video_url: str | None = None
    comentario: str | None = None


class InstanciaEncuentroListResponse(BaseModel):
    items: list[InstanciaEncuentroResponse]
    total: int
    pagina: int
    page_size: int


class CrearSlotRecurrenteRequest(BaseModel):
    materia_id: str
    titulo: str
    hora: time
    dia_semana: str
    fecha_inicio: date
    cant_semanas: int = 0
    fecha_unica: date | None = None
    meet_url: str
    vig_desde: date
    vig_hasta: date | None = None


class CrearEncuentroUnicoRequest(BaseModel):
    materia_id: str
    fecha: date
    hora: time
    titulo: str
    meet_url: str = ""
    video_url: str | None = None
    comentario: str | None = None


class EditarInstanciaRequest(BaseModel):
    estado: str | None = None
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None


class GenerarHTMLResponse(BaseModel):
    html: str
