from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import EntityMeta


class User(Base, EntityMeta):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(500), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(String(32), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    apellidos: Mapped[str | None] = mapped_column(String(200), nullable=True)
    dni: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cuil: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cbu: Mapped[str | None] = mapped_column(String(500), nullable=True)
    alias_cbu: Mapped[str | None] = mapped_column(String(500), nullable=True)
    banco: Mapped[str | None] = mapped_column(String(100), nullable=True)
    regional: Mapped[str | None] = mapped_column(String(100), nullable=True)
    legajo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    legajo_profesional: Mapped[str | None] = mapped_column(String(50), nullable=True)
    facturador: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="Activo", nullable=False)

    roles: Mapped[list["Rol"]] = relationship(  # noqa: F821
        secondary="user_roles", lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_user_email_per_tenant"),
    )
