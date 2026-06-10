"""create comunicacion table and add requires_aprobacion to tenant

Revision ID: 009
Revises: 008
Create Date: 2026-06-10

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "009"
down_revision: str | None = "008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comunicacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enviado_por", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("destinatario", sa.String(500), nullable=False),
        sa.Column("asunto", sa.String(200), nullable=False),
        sa.Column("cuerpo", sa.Text, nullable=False),
        sa.Column("lote_id", UUID(as_uuid=True), nullable=True),
        sa.Column("intentos", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("error_msg", sa.Text, nullable=True),
        sa.Column("estado", sa.String(30), nullable=False, server_default=sa.text("'Nueva'")),
        sa.Column("enviado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enqueue_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_comunicacion_lote_id", "comunicacion", ["lote_id"])
    op.create_index("ix_comunicacion_estado", "comunicacion", ["estado"])

    op.add_column(
        "tenant",
        sa.Column("requiere_aprobacion_comunicaciones", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("tenant", "requiere_aprobacion_comunicaciones")
    op.drop_index("ix_comunicacion_estado", table_name="comunicacion")
    op.drop_index("ix_comunicacion_lote_id", table_name="comunicacion")
    op.drop_table("comunicacion")
