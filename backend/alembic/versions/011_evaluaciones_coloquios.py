"""create evaluacion, evaluacion_dia, reserva_evaluacion,
resultado_evaluacion, evaluacion_alumno tables

Revision ID: 011
Revises: 010
Create Date: 2026-06-11

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "011"
down_revision: str | None = "010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohortes.id"), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("instancia", sa.String(200), nullable=False),
        sa.Column("dias_disponibles", sa.Integer, nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Activa'")),
    )

    op.create_table(
        "evaluacion_dia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id"), nullable=False),
        sa.Column("fecha", sa.Date, nullable=False),
        sa.Column("cupo_maximo", sa.Integer, nullable=False),
        sa.Column("cupos_restantes", sa.Integer, nullable=False),
    )

    op.create_table(
        "reserva_evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluacion_dia_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion_dia.id"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Activa'")),
    )

    op.create_table(
        "resultado_evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("nota_final", sa.String(20), nullable=False),
    )

    op.create_table(
        "evaluacion_alumno",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("evaluacion_id", "alumno_id", name="uq_evaluacion_alumno"),
    )

    op.create_index("ix_evaluacion_materia_id", "evaluacion", ["materia_id"])
    op.create_index("ix_evaluacion_dia_evaluacion_id", "evaluacion_dia", ["evaluacion_id"])
    op.create_index("ix_reserva_evaluacion_alumno_id", "reserva_evaluacion", ["alumno_id"])
    op.create_index("ix_reserva_evaluacion_evaluacion_dia_id", "reserva_evaluacion", ["evaluacion_dia_id"])
    op.create_index("ix_resultado_evaluacion_evaluacion_id", "resultado_evaluacion", ["evaluacion_id"])
    op.create_index("ix_evaluacion_alumno_evaluacion_id", "evaluacion_alumno", ["evaluacion_id"])


def downgrade() -> None:
    op.drop_table("evaluacion_alumno")
    op.drop_table("resultado_evaluacion")
    op.drop_table("reserva_evaluacion")
    op.drop_table("evaluacion_dia")
    op.drop_table("evaluacion")
