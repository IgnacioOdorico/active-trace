import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class Asignacion(Base, EntityMeta):
    __tablename__ = "asignaciones"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    rol: Mapped[str] = mapped_column(String(50), nullable=False)
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materias.id"), nullable=True
    )
    carrera_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("carreras.id"), nullable=True
    )
    cohorte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=True
    )
    comisiones: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    desde: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hasta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def estado_vigencia(self) -> str:
        now = (
            datetime.now(self.desde.tzinfo)
            if self.desde and self.desde.tzinfo
            else datetime.now()
        )
        if self.desde and now < self.desde:
            return "Pendiente"
        if self.hasta and now >= self.hasta:
            return "Vencida"
        return "Vigente"
