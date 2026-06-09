"""alter users (add PII fields) + create asignaciones table

Revision ID: 006
Revises: 005
Create Date: 2026-06-08

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("nombre", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("apellidos", sa.String(200), nullable=True))
    op.add_column("users", sa.Column("dni", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("cuil", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("cbu", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("alias_cbu", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("banco", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("regional", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("legajo", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("legajo_profesional", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("facturador", sa.Boolean, nullable=False, server_default=sa.text("false")))
    op.add_column("users", sa.Column("estado", sa.String(20), nullable=False, server_default="Activo"))

    op.alter_column("users", "email", type_=sa.String(500), existing_type=sa.String(255), nullable=False)
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=True)

    op.create_table(
        "asignaciones",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("rol", sa.String(50), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=True),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carreras.id"), nullable=True),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohortes.id"), nullable=True),
        sa.Column("comisiones", ARRAY(sa.String), nullable=True),
        sa.Column("responsable_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("desde", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hasta", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_asignaciones_tenant_usuario", "asignaciones", ["tenant_id", "usuario_id"])
    op.create_index("ix_asignaciones_tenant_rol", "asignaciones", ["tenant_id", "rol"])
    op.create_index("ix_asignaciones_tenant_materia", "asignaciones", ["tenant_id", "materia_id"])


def downgrade() -> None:
    op.drop_index("ix_asignaciones_tenant_materia")
    op.drop_index("ix_asignaciones_tenant_rol")
    op.drop_index("ix_asignaciones_tenant_usuario")
    op.drop_table("asignaciones")

    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=False)
    op.alter_column("users", "email", type_=sa.String(255), existing_type=sa.String(500), nullable=False)
    op.drop_column("users", "estado")
    op.drop_column("users", "facturador")
    op.drop_column("users", "legajo_profesional")
    op.drop_column("users", "legajo")
    op.drop_column("users", "regional")
    op.drop_column("users", "banco")
    op.drop_column("users", "alias_cbu")
    op.drop_column("users", "cbu")
    op.drop_column("users", "cuil")
    op.drop_column("users", "dni")
    op.drop_column("users", "apellidos")
    op.drop_column("users", "nombre")
