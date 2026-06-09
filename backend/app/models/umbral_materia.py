import uuid

from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class UmbralMateria(Base, EntityMeta):
    __tablename__ = "umbral_materia"

    asignacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asignaciones.id"), nullable=False, unique=True
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materias.id"), nullable=False
    )
    umbral_pct: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    valores_aprobatorios: Mapped[dict | None] = mapped_column(JSON, nullable=True)
