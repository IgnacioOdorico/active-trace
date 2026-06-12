"""create programa_materia and fecha_academica tables

Revision ID: 014
Revises: 013
Create Date: 2026-06-12

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "014"
down_revision: str | None = "013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "programa_materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carreras.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohortes.id"), nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("referencia_archivo", sa.String(500), nullable=False),
        sa.Column("cargado_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "fecha_academica",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohortes.id"), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("numero", sa.Integer, nullable=False),
        sa.Column("periodo", sa.String(20), nullable=False),
        sa.Column("fecha", sa.Date, nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
    )

    op.create_index("ix_programa_materia_materia_id", "programa_materia", ["materia_id"])
    op.create_index("ix_fecha_academica_materia_id", "fecha_academica", ["materia_id"])


def downgrade() -> None:
    op.drop_index("ix_fecha_academica_materia_id", table_name="fecha_academica")
    op.drop_index("ix_programa_materia_materia_id", table_name="programa_materia")
    op.drop_table("fecha_academica")
    op.drop_table("programa_materia")
