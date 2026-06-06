import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import EntityMeta


class Materia(Base, EntityMeta):
    __tablename__ = "materias"

    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    carrera_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("carreras.id"), nullable=True
    )

    carrera: Mapped["Carrera | None"] = relationship(back_populates="materias")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo", name="uq_materia_codigo_tenant"),
    )
