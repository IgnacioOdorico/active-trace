from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    materia_id: str
    cohorte_id: str
    tipo: str
    instancia: str
    dias_disponibles: int
    total_convocados: int = 0
    total_reservas_activas: int = 0
    total_cupos_libres: int = 0


class EvaluacionDiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evaluacion_id: str
    fecha: date
    cupo_maximo: int
    cupos_restantes: int


class ReservaEvaluacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evaluacion_dia_id: str
    alumno_id: str
    fecha_hora: datetime
    estado: str
    evaluacion_materia: str | None = None
    evaluacion_instancia: str | None = None
    dia_fecha: date | None = None


class ResultadoEvaluacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evaluacion_id: str
    alumno_id: str
    nota_final: str
    alumno_nombre: str | None = None
    alumno_apellido: str | None = None


class CrearEvaluacionRequest(BaseModel):
    materia_id: str
    cohorte_id: str
    tipo: str = Field(pattern=r"^(Parcial|TP|Coloquio|Recuperatorio)$")
    instancia: str
    dias_disponibles: int = Field(ge=1)
    cupo_por_dia: int = Field(ge=1)


class ImportarAlumnosRequest(BaseModel):
    alumno_ids: list[str]


class ReservarTurnoRequest(BaseModel):
    evaluacion_dia_id: str


class RegistrarResultadoRequest(BaseModel):
    alumno_id: str
    nota_final: str


class MetricasResponse(BaseModel):
    total_alumnos_convocados: int
    total_instancias_activas: int
    total_reservas_activas: int
    total_notas_registradas: int


class MetricasConvocatoriaResponse(BaseModel):
    convocados: int
    reservas_activas: int
    cupos_libres: int
    notas_registradas: int


class AgendaResponse(BaseModel):
    reserva_id: str
    alumno_nombre: str
    alumno_apellido: str
    alumno_email: str | None = None
    fecha_reserva: date | None = None
    hora_reserva: datetime | None = None


class ConvocatoriaDisponibleResponse(BaseModel):
    id: str
    materia_nombre: str | None = None
    instancia: str
    tipo: str
    dias_restantes_con_cupo: int


class EvaluacionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    materia_id: str
    cohorte_id: str
    tipo: str
    instancia: str
    dias_disponibles: int
    created_at: datetime


class EvaluacionListResponse(BaseModel):
    items: list[EvaluacionResponse]
    total: int
    pagina: int
    page_size: int
