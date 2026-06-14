import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class AlcanceAviso(StrEnum):
    GLOBAL = "Global"
    POR_MATERIA = "PorMateria"
    POR_COHORTE = "PorCohorte"
    POR_ROL = "PorRol"


class SeveridadAviso(StrEnum):
    INFO = "Info"
    ADVERTENCIA = "Advertencia"
    CRITICO = "Crítico"


class Aviso(Base, EntityMeta):
    __tablename__ = "aviso"

    alcance: Mapped[str] = mapped_column(String(20), nullable=False)
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materias.id"), nullable=True
    )
    cohorte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=True
    )
    rol_destino: Mapped[str | None] = mapped_column(String(20), nullable=True)
    severidad: Mapped[str] = mapped_column(String(20), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    inicio_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    fin_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requiere_ack: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
