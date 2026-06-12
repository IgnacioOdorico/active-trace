import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class ProgramaMateria(Base, EntityMeta):
    __tablename__ = "programa_materia"

    materia_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("materias.id"), nullable=False
    )
    carrera_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("carreras.id"), nullable=False
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cohortes.id"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    referencia_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    cargado_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
