import uuid

from pydantic import BaseModel


class ActividadProblematica(BaseModel):
    nombre_actividad: str
    motivo: str


class AlumnoAtrasadoResponse(BaseModel):
    entrada_padron_id: str
    nombre: str
    apellidos: str
    email: str
    comision: str | None = None
    actividades_problematicas: list[ActividadProblematica]


class RankingItemResponse(BaseModel):
    entrada_padron_id: str
    nombre: str
    apellidos: str
    comision: str | None = None
    actividades_aprobadas: int
    total_actividades: int


class ReportesResponse(BaseModel):
    total_alumnos: int
    total_actividades: int
    total_calificaciones: int
    promedio_aprobacion_general: float | None = None
    alumnos_atrasados_count: int
    alumnos_aprobados_count: int
    sin_datos: bool = False


class NotaActividad(BaseModel):
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None


class NotaFinalItemResponse(BaseModel):
    entrada_padron_id: str
    nombre: str
    apellidos: str
    comision: str | None = None
    notas: list[NotaActividad]
    nota_final: float | None = None
    actividades_textuales: list[str] = []
    estado: str


class NotasFinalesRequest(BaseModel):
    materia_id: uuid.UUID
    actividades: list[str]


class MonitorItemResponse(BaseModel):
    entrada_padron_id: str
    nombre: str
    apellidos: str
    email: str
    comision: str | None = None
    regional: str | None = None
    materia_id: str | None = None
    total_actividades: int
    aprobadas: int
    estado: str


class MonitorPaginationResponse(BaseModel):
    items: list[MonitorItemResponse]
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int
