import uuid
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class EstadoReserva(StrEnum):
    ACTIVA = "Activa"
    CANCELADA = "Cancelada"


class ReservaEvaluacion(Base, EntityMeta):
    __tablename__ = "reserva_evaluacion"

    evaluacion_dia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evaluacion_dia.id"), nullable=False
    )
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    fecha_hora: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    estado: Mapped[str] = mapped_column(
        String(20), default=EstadoReserva.ACTIVA, nullable=False
    )
