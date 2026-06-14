from datetime import date

from pydantic import BaseModel

from app.schemas.audit import AuditLogResponse


class AccionesPorDiaItem(BaseModel):
    fecha: date
    total: int


class ComunicacionesPorDocenteItem(BaseModel):
    docente_id: str
    docente_nombre: str = ""
    pendiente: int = 0
    enviando: int = 0
    enviado: int = 0
    fallido: int = 0
    cancelado: int = 0


class InteraccionesPorDocenteMateriaItem(BaseModel):
    docente_id: str
    docente_nombre: str = ""
    materia_id: str
    materia_nombre: str = ""
    total_acciones: int
    acciones_por_tipo: dict


class UltimasAccionesResponse(BaseModel):
    items: list[AuditLogResponse]
    max_resultados: int
