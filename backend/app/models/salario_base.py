from datetime import date

from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import EntityMeta


class SalarioBase(Base, EntityMeta):
    __tablename__ = "salarios_base"

    rol: Mapped[str] = mapped_column(String(50), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    desde: Mapped[date] = mapped_column(Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
