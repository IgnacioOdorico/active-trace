import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import EntityMeta


class Cohorte(Base, EntityMeta):
    __tablename__ = "cohortes"

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    carrera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carreras.id"), nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    carrera: Mapped["Carrera"] = relationship(back_populates="cohortes")  # noqa: F821

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "carrera_id", "nombre", name="uq_cohorte_nombre_carrera_tenant"
        ),
    )
