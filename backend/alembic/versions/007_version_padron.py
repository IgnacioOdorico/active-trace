"""create version_padron and entrada_padron tables

Revision ID: 007
Revises: 006
Create Date: 2026-06-09

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "007"
down_revision: str | None = "006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "version_padron",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohortes.id"), nullable=False),
        sa.Column("cargado_por", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    op.create_index(
        "uq_version_padron_activa",
        "version_padron",
        ["materia_id", "cohorte_id"],
        unique=True,
        postgresql_where=sa.text("activa = true"),
    )

    op.create_table(
        "entrada_padron",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version_id", UUID(as_uuid=True), sa.ForeignKey("version_padron.id"), nullable=False, index=True),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("apellidos", sa.String(200), nullable=False),
        sa.Column("email", sa.String(500), nullable=False),
        sa.Column("comision", sa.String(50), nullable=True),
        sa.Column("regional", sa.String(100), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("entrada_padron")
    op.drop_index("uq_version_padron_activa", table_name="version_padron")
    op.drop_table("version_padron")
