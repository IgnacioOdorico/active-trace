import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class Calificacion(Base, EntityMeta):
    __tablename__ = "calificacion"

    entrada_padron_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entrada_padron.id"), nullable=False, index=True
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materias.id"), nullable=False
    )
    nombre_actividad: Mapped[str] = mapped_column(String(200), nullable=False)
    nota_numerica: Mapped[float | None] = mapped_column(Float, nullable=True)
    nota_textual: Mapped[str | None] = mapped_column(String(200), nullable=True)
    aprobado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    origen: Mapped[str] = mapped_column(String(20), nullable=False)
    importado_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "entrada_padron_id",
            "nombre_actividad",
            name="uq_calificacion_entrada_actividad",
        ),
    )
