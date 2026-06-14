import uuid
from datetime import date
from enum import Enum

from sqlalchemy import Date, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class TipoFechaAcademica(str, Enum):
    PARCIAL = "Parcial"
    TP = "TP"
    COLOQUIO = "Coloquio"
    RECUPERATORIO = "Recuperatorio"


class FechaAcademica(Base, EntityMeta):
    __tablename__ = "fecha_academica"

    materia_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("materias.id"), nullable=False
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cohortes.id"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    periodo: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
