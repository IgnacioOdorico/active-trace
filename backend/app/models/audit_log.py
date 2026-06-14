import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id"),
        nullable=False,
    )
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    impersonado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=True,
    )
    accion: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    detalle: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    filas_afectadas: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    ip: Mapped[str | None] = mapped_column(
        String(45), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    actor: Mapped["User"] = relationship(
        "User", foreign_keys=[actor_id], lazy="selectin",
    )
    impersonado: Mapped["User | None"] = relationship(
        "User", foreign_keys=[impersonado_id], lazy="selectin",
    )
    materia: Mapped["Materia | None"] = relationship(
        "Materia", foreign_keys=[materia_id], lazy="selectin",
    )
