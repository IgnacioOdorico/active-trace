"""create aviso and acknowledgment_aviso tables + seed permisos

Revision ID: 012
Revises: 011
Create Date: 2026-06-11

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import table, column

revision: str = "012"
down_revision: str | None = "011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "aviso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("alcance", sa.String(20), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materias.id"), nullable=True),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohortes.id"), nullable=True),
        sa.Column("rol_destino", sa.String(20), nullable=True),
        sa.Column("severidad", sa.String(20), nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("cuerpo", sa.Text, nullable=False),
        sa.Column("inicio_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fin_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("orden", sa.Integer, nullable=False),
        sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("requiere_ack", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    op.create_table(
        "acknowledgment_aviso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("aviso_id", UUID(as_uuid=True), sa.ForeignKey("aviso.id"), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("confirmado_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index("ix_aviso_tenant_activo_vigencia", "aviso", ["tenant_id", "activo", "inicio_en", "fin_en"])
    op.create_index("ix_acknowledgment_aviso_aviso_usuario", "acknowledgment_aviso", ["aviso_id", "usuario_id"], unique=True)
    op.create_index("ix_acknowledgment_aviso_aviso_id", "acknowledgment_aviso", ["aviso_id"])

    # Seed permission codes for avisos
    conn = op.get_bind()

    PERMISO_CODES = ["avisos:publicar"]
    PERMISO_DESCRIPTIONS = {
        "avisos:publicar": "Publicar y gestionar avisos",
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

        # Assign to COORDINADOR and ADMIN
        for rol_codigo in ("COORDINADOR", "ADMIN"):
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
    op.drop_table("acknowledgment_aviso")
    op.drop_table("aviso")
