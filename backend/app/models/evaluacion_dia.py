import uuid

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class EvaluacionDia(Base, EntityMeta):
    __tablename__ = "evaluacion_dia"

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evaluacion.id"), nullable=False
    )
    fecha: Mapped[str] = mapped_column(Date, nullable=False)
    cupo_maximo: Mapped[int] = mapped_column(Integer, nullable=False)
    cupos_restantes: Mapped[int] = mapped_column(Integer, nullable=False)
