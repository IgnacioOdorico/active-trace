"""create mensajes table + seed permisos perfil:editar, inbox:leer, inbox:responder

Revision ID: 016
Revises: 43b9103973c5
Create Date: 2026-06-12

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import table, column

revision: str = "016"
down_revision: str | None = "43b9103973c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "mensajes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("thread_id", UUID(as_uuid=True), sa.ForeignKey("mensajes.id"), nullable=True),
        sa.Column("remitente_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("destinatario_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("asunto", sa.String(200), nullable=False),
        sa.Column("cuerpo", sa.Text, nullable=False),
        sa.Column("leido", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    op.create_index("ix_mensajes_destinatario_thread", "mensajes", ["destinatario_id", "thread_id"])
    op.create_index("ix_mensajes_thread_id", "mensajes", ["thread_id"])

    # Seed permissions
    conn = op.get_bind()

    PERMISO_CODES = ["perfil:editar", "inbox:leer", "inbox:responder"]
    PERMISO_DESCRIPTIONS = {
        "perfil:editar": "Editar perfil propio",
        "inbox:leer": "Leer mensajes de la bandeja de entrada",
        "inbox:responder": "Responder mensajes de la bandeja de entrada",
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

    ROLE_ASSIGNMENTS = ["TUTOR", "PROFESOR", "COORDINADOR", "ADMIN"]

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

        for rol_codigo in ROLE_ASSIGNMENTS:
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
    op.drop_table("mensajes")
