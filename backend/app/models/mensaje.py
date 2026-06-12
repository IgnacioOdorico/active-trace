import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import EntityMeta


class Mensaje(Base, EntityMeta):
    __tablename__ = "mensajes"

    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mensajes.id"), nullable=True, index=True
    )
    remitente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    destinatario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    asunto: Mapped[str] = mapped_column(String(200), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    leido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    remitente: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[remitente_id], lazy="selectin"
    )
    destinatario: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[destinatario_id], lazy="selectin"
    )
