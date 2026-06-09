import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class EntradaPadron(Base, EntityMeta):
    __tablename__ = "entrada_padron"

    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("version_padron.id"),
        nullable=False,
        index=True,
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(500), nullable=False)
    comision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    regional: Mapped[str | None] = mapped_column(String(100), nullable=True)
