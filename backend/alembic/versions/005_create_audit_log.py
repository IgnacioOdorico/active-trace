"""create audit_log table

Revision ID: 005
Revises: 004
Create Date: 2026-06-08

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("impersonado_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=True),
        sa.Column("accion", sa.String(100), nullable=False),
        sa.Column("detalle", sa.JSON, nullable=True),
        sa.Column("filas_afectadas", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
    )

    op.create_index(
        "ix_audit_log_tenant_accion",
        "audit_log",
        ["tenant_id", "accion"],
    )
    op.create_index(
        "ix_audit_log_tenant_actor",
        "audit_log",
        ["tenant_id", "actor_id"],
    )
    op.create_index(
        "ix_audit_log_tenant_fecha_hora",
        "audit_log",
        ["tenant_id", "fecha_hora"],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_log_tenant_fecha_hora")
    op.drop_index("ix_audit_log_tenant_actor")
    op.drop_index("ix_audit_log_tenant_accion")
    op.drop_table("audit_log")
