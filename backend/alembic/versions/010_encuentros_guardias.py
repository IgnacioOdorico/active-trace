"""create slot_encuentro, instancia_encuentro, guardia tables

Revision ID: 010
Revises: 009
Create Date: 2026-06-10

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "010"
down_revision: str | None = "009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "slot_encuentro",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignaciones.id"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("hora", sa.Time, nullable=False),
        sa.Column("dia_semana", sa.String(15), nullable=False),
        sa.Column("fecha_inicio", sa.Date, nullable=False),
        sa.Column("cant_semanas", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("fecha_unica", sa.Date, nullable=True),
        sa.Column("meet_url", sa.String(500), nullable=False),
        sa.Column("vig_desde", sa.Date, nullable=False),
        sa.Column("vig_hasta", sa.Date, nullable=True),
    )

    op.create_table(
        "instancia_encuentro",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("slot_id", UUID(as_uuid=True), sa.ForeignKey("slot_encuentro.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("fecha", sa.Date, nullable=False),
        sa.Column("hora", sa.Time, nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Programado'")),
        sa.Column("meet_url", sa.String(500), nullable=False),
        sa.Column("video_url", sa.String(500), nullable=True),
        sa.Column("comentario", sa.Text, nullable=True),
    )

    op.create_table(
        "guardia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignaciones.id"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carreras.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohortes.id"), nullable=True),
        sa.Column("dia", sa.String(15), nullable=False),
        sa.Column("horario", sa.String(20), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Pendiente'")),
        sa.Column("comentarios", sa.Text, nullable=True),
    )

    op.create_index("ix_instancia_encuentro_materia_id", "instancia_encuentro", ["materia_id"])
    op.create_index("ix_instancia_encuentro_estado", "instancia_encuentro", ["estado"])
    op.create_index("ix_guardia_materia_id", "guardia", ["materia_id"])
    op.create_index("ix_guardia_asignacion_id", "guardia", ["asignacion_id"])


def downgrade() -> None:
    op.drop_index("ix_guardia_asignacion_id", table_name="guardia")
    op.drop_index("ix_guardia_materia_id", table_name="guardia")
    op.drop_index("ix_instancia_encuentro_estado", table_name="instancia_encuentro")
    op.drop_index("ix_instancia_encuentro_materia_id", table_name="instancia_encuentro")
    op.drop_table("guardia")
    op.drop_table("instancia_encuentro")
    op.drop_table("slot_encuentro")
