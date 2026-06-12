from app.repositories.acknowledgment_aviso_repository import AcknowledgmentAvisoRepository
from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.repositories.aviso_repository import AvisoRepository
from app.repositories.comentario_tarea_repository import ComentarioTareaRepository
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.repositories.evaluacion_alumno_repository import EvaluacionAlumnoRepository
from app.repositories.evaluacion_dia_repository import EvaluacionDiaRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.guardia_repository import GuardiaRepository
from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
from app.repositories.reserva_evaluacion_repository import ReservaEvaluacionRepository
from app.repositories.resultado_evaluacion_repository import ResultadoEvaluacionRepository
from app.repositories.slot_encuentro_repository import SlotEncuentroRepository
from app.repositories.tarea_repository import TareaRepository

__all__ = [
    "AcknowledgmentAvisoRepository",
    "AvisoRepository",
    "FechaAcademicaRepository",
    "ProgramaMateriaRepository",
    "ComentarioTareaRepository",
    "ComunicacionRepository",
    "EvaluacionAlumnoRepository",
    "EvaluacionDiaRepository",
    "EvaluacionRepository",
    "GuardiaRepository",
    "InstanciaEncuentroRepository",
    "ReservaEvaluacionRepository",
    "ResultadoEvaluacionRepository",
    "SlotEncuentroRepository",
    "TareaRepository",
]
