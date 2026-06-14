import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class TipoEvaluacion(StrEnum):
    PARCIAL = "Parcial"
    TP = "TP"
    COLOQUIO = "Coloquio"
    RECUPERATORIO = "Recuperatorio"


class Evaluacion(Base, EntityMeta):
    __tablename__ = "evaluacion"

    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materias.id"), nullable=False
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    instancia: Mapped[str] = mapped_column(String(200), nullable=False)
    dias_disponibles: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default="Activa", nullable=False
    )
