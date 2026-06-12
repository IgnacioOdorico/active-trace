from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.asignacion import Asignacion
from app.models.aviso import AlcanceAviso, Aviso, SeveridadAviso
from app.models.audit_log import AuditLog
from app.models.base import EntityMeta
from app.models.calificacion import Calificacion
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.evaluacion import Evaluacion, TipoEvaluacion
from app.models.evaluacion_alumno import EvaluacionAlumno
from app.models.evaluacion_dia import EvaluacionDia
from app.models.guardia import EstadoGuardia, Guardia
from app.models.instancia_encuentro import EstadoEncuentro, InstanciaEncuentro
from app.models.materia import Materia
from app.models.permiso import Permiso
from app.models.recovery_token import RecoveryToken
from app.models.refresh_token import RefreshToken
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.slot_encuentro import DiaSemana, SlotEncuentro
from app.models.tarea import EstadoTarea, Tarea
from app.models.comentario_tarea import ComentarioTarea
from app.models.fecha_academica import FechaAcademica, TipoFechaAcademica
from app.models.programa_materia import ProgramaMateria
from app.models.tenant import Tenant
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.user_rol import UserRol
from app.models.version_padron import VersionPadron

__all__ = [
    "AcknowledgmentAviso",
    "AlcanceAviso",
    "Asignacion",
    "Aviso",
    "AuditLog",
    "Calificacion",
    "Carrera",
    "Comunicacion",
    "DiaSemana",
    "EstadoComunicacion",
    "EstadoEncuentro",
    "EstadoGuardia",
    "EstadoReserva",
    "Cohorte",
    "ComentarioTarea",
    "EntradaPadron",
    "EstadoTarea",
    "EntityMeta",
    "FechaAcademica",
    "ProgramaMateria",
    "TipoFechaAcademica",
    "Evaluacion",
    "EvaluacionAlumno",
    "EvaluacionDia",
    "Guardia",
    "InstanciaEncuentro",
    "Materia",
    "Permiso",
    "RecoveryToken",
    "RefreshToken",
    "ReservaEvaluacion",
    "ResultadoEvaluacion",
    "Rol",
    "RolPermiso",
    "SlotEncuentro",
    "Tarea",
    "Tenant",
    "TipoEvaluacion",
    "UmbralMateria",
    "User",
    "UserRol",
    "VersionPadron",
]
