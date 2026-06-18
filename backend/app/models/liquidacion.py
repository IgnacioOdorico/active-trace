import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.financial_base import FinancialEntityMeta


class Liquidacion(Base, FinancialEntityMeta):
    __tablename__ = "liquidaciones"

    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=False
    )
    periodo: Mapped[str] = mapped_column(String(7), nullable=False)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    rol: Mapped[str] = mapped_column(String(50), nullable=False)
    comisiones: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    monto_base: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    monto_plus: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    es_nexo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    excluido_por_factura: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    estado: Mapped[str] = mapped_column(
        String(20), default="Abierta", nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
