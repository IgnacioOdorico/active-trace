"""create tarea and comentario_tarea tables + seed permisos

Revision ID: 013
Revises: 012
Create Date: 2026-06-11

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import table, column

revision: str = "013"
down_revision: str | None = "012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tarea",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=True),
        sa.Column("asignado_a", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("asignado_por", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Pendiente'")),
        sa.Column("descripcion", sa.Text, nullable=False),
        sa.Column("contexto_id", UUID(as_uuid=True), nullable=True),
    )

    op.create_table(
        "comentario_tarea",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tarea_id", UUID(as_uuid=True), sa.ForeignKey("tarea.id"), nullable=False),
        sa.Column("autor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("texto", sa.Text, nullable=False),
        sa.Column("creado_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_tarea_tenant_estado", "tarea", ["tenant_id", "estado"])
    op.create_index("ix_tarea_asignado_a", "tarea", ["asignado_a"])
    op.create_index("ix_comentario_tarea_tarea_id", "comentario_tarea", ["tarea_id"])

    # Seed permission codes for tareas
    conn = op.get_bind()

    PERMISO_CODES = ["tareas:gestionar"]
    PERMISO_DESCRIPTIONS = {
        "tareas:gestionar": "Gestionar tareas internas",
    }

    permisos_table = table(
        "permisos",
        column("id", UUID),
        column("codigo", sa.String),
        column("nombre", sa.String),
        column("descripcion", sa.Text),
        column("modulo", sa.String),
        column("propio", sa.Boolean),
    )

    for codigo in PERMISO_CODES:
        module = codigo.split(":", 1)[0]
        propio = "(propio)" in codigo
        nombre = f"{module.capitalize()} - {codigo.split(':', 1)[1].replace('(propio)', '').capitalize().strip()}"
        op.execute(
            permisos_table.insert().values(
                codigo=codigo,
                nombre=nombre,
                descripcion=PERMISO_DESCRIPTIONS.get(codigo),
                modulo=module,
                propio=propio,
            )
        )

        perm_row = conn.execute(
            sa.text("SELECT id FROM permisos WHERE codigo = :codigo"),
            {"codigo": codigo},
        ).fetchone()
        if perm_row is None:
            continue
        perm_uuid = perm_row[0]

        for rol_codigo in ("PROFESOR", "COORDINADOR", "ADMIN"):
            rol_row = conn.execute(
                sa.text("SELECT id FROM roles WHERE codigo = :codigo"),
                {"codigo": rol_codigo},
            ).fetchone()
            if rol_row is None:
                continue
            rol_uuid = rol_row[0]

            rp_table = table(
                "rol_permisos",
                column("id", UUID),
                column("rol_id", UUID),
                column("permiso_id", UUID),
            )
            op.execute(
                rp_table.insert().values(
                    rol_id=rol_uuid,
                    permiso_id=perm_uuid,
                )
            )


def downgrade() -> None:
    op.drop_table("comentario_tarea")
    op.drop_table("tarea")
