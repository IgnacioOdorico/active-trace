import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class ResultadoEvaluacion(Base, EntityMeta):
    __tablename__ = "resultado_evaluacion"

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evaluacion.id"), nullable=False
    )
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    nota_final: Mapped[str] = mapped_column(String(20), nullable=False)
