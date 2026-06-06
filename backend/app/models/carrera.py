from sqlalchemy import Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import EntityMeta


class Carrera(Base, EntityMeta):
    __tablename__ = "carreras"

    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    cohortes: Mapped[list["Cohorte"]] = relationship(back_populates="carrera")  # noqa: F821
    materias: Mapped[list["Materia"]] = relationship(back_populates="carrera")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo", name="uq_carrera_codigo_tenant"),
    )
