import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRol(Base):
    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    rol_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "rol_id", name="uq_user_rol"),
    )
