from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import RootEntityMeta


class Tenant(Base, RootEntityMeta):
    __tablename__ = "tenant"

    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default={}, server_default="{}"
    )
    requiere_aprobacion_comunicaciones: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
