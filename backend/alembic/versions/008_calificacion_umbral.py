"""create calificacion and umbral_materia tables

Revision ID: 008
Revises: 007
Create Date: 2026-06-09

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "008"
down_revision: str | None = "007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calificacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entrada_padron_id", UUID(as_uuid=True), sa.ForeignKey("entrada_padron.id"), nullable=False, index=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("nombre_actividad", sa.String(200), nullable=False),
        sa.Column("nota_numerica", sa.Float, nullable=True),
        sa.Column("nota_textual", sa.String(200), nullable=True),
        sa.Column("aprobado", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("origen", sa.String(20), nullable=False),
        sa.Column("importado_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_unique_constraint(
        "uq_calificacion_entrada_actividad",
        "calificacion",
        ["entrada_padron_id", "nombre_actividad"],
    )

    op.create_table(
        "umbral_materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignaciones.id"), nullable=False, unique=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("umbral_pct", sa.Float, nullable=False, server_default=sa.text("60.0")),
        sa.Column("valores_aprobatorios", JSON, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("umbral_materia")
    op.drop_constraint("uq_calificacion_entrada_actividad", "calificacion")
    op.drop_table("calificacion")
