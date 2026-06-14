"""create roles, permisos, rol_permisos, user_roles tables + seed data

Revision ID: 003
Revises: 002
Create Date: 2026-06-06

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import table, column

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SEED_ROLES: dict[str, dict[str, str | None]] = {
    "ADMIN": {"nombre": "Administrador", "descripcion": "Acceso total al sistema"},
    "COORDINADOR": {"nombre": "Coordinador", "descripcion": "Gestión académica y administrativa"},
    "PROFESOR": {"nombre": "Profesor", "descripcion": "Gestión de calificaciones y comunicaciones"},
    "TUTOR": {"nombre": "Tutor", "descripcion": "Seguimiento de alumnos"},
    "ALUMNO": {"nombre": "Alumno", "descripcion": "Acceso a perfil y coloquios"},
    "NEXO": {"nombre": "Nexo", "descripcion": "Gestión de liquidaciones y facturas"},
    "FINANZAS": {"nombre": "Finanzas", "descripcion": "Gestión financiera completa"},
}

SEED_ROLE_PERMS: dict[str, list[str]] = {
    "ADMIN": ["*:*"],
    "COORDINADOR": [
        "estructura:*", "equipos:*", "avisos:*", "encuentros:*", "encuentros:gestionar",
        "coloquios:*", "tareas:*", "padron:ver", "atrasados:ver",
        "auditoria:ver", "auditoria:ver(propio)",
        "calificaciones:ver", "comunicaciones:*", "programas:*",
    ],
    "PROFESOR": [
        "calificaciones:*", "padron:ver", "atrasados:ver",
        "comunicaciones:enviar", "comunicaciones:ver(propio)",
        "encuentros:ver(propio)", "tareas:*(propio)",
    ],
    "TUTOR": [
        "atrasados:ver", "encuentros:ver(propio)", "guardias:registrar",
    ],
    "ALUMNO": [
        "coloquios:reservar", "perfil:ver(propio)", "mensajes:*(propio)",
    ],
    "NEXO": [
        "liquidaciones:ver", "facturas:ver",
    ],
    "FINANZAS": [
        "liquidaciones:*", "facturas:*",
    ],
}

PERMISO_DESCRIPTIONS: dict[str, str] = {
    "estructura:*": "Gestionar estructura organizativa",
    "equipos:*": "Gestionar equipos de trabajo",
    "avisos:*": "Gestionar avisos y notificaciones",
    "encuentros:*": "Gestionar encuentros",
    "encuentros:gestionar": "Gestionar encuentros y guardias",
    "encuentros:ver(propio)": "Ver encuentros propios",
    "coloquios:*": "Gestionar coloquios",
    "coloquios:reservar": "Reservar coloquios",
    "tareas:*": "Gestionar tareas",
    "tareas:*(propio)": "Gestionar tareas propias",
    "padron:ver": "Ver padrón",
    "atrasados:ver": "Ver atrasados",
    "auditoria:ver": "Ver auditoría",
    "auditoria:ver(propio)": "Ver auditoría propia",
    "calificaciones:*": "Gestionar calificaciones",
    "calificaciones:ver": "Ver calificaciones",
    "comunicaciones:*": "Gestionar comunicaciones",
    "comunicaciones:enviar": "Enviar comunicaciones",
    "comunicaciones:ver(propio)": "Ver comunicaciones propias",
    "programas:*": "Gestionar programas",
    "guardias:registrar": "Registrar guardias",
    "perfil:ver(propio)": "Ver perfil propio",
    "mensajes:*(propio)": "Gestionar mensajes propios",
    "liquidaciones:*": "Gestionar liquidaciones",
    "liquidaciones:ver": "Ver liquidaciones",
    "facturas:*": "Gestionar facturas",
    "facturas:ver": "Ver facturas",
    "*:*": "Acceso total al sistema",
    "impersonacion:usar": "Usar impersonación",
}


def _get_perm_nombre(codigo: str) -> str:
    module = codigo.split(":", 1)[0]
    action_part = codigo.split(":", 1)[1] if ":" in codigo else ""
    if codigo == "*:*":
        return "Acceso total"
    if codigo.endswith("(*)"):
        return f"{module.capitalize()} - {action_part.replace('(*)', '').capitalize()} (propio)"
    return f"{module.capitalize()} - {action_part.capitalize()}"


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("codigo", sa.String(50), unique=True, nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "permisos",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("codigo", sa.String(100), unique=True, nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("modulo", sa.String(50), nullable=False),
        sa.Column("propio", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "rol_permisos",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("rol_id", UUID, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("permiso_id", UUID, sa.ForeignKey("permisos.id"), nullable=False),
        sa.Column("ambito", sa.String(20), nullable=True),
        sa.UniqueConstraint("rol_id", "permiso_id", name="uq_rol_permiso"),
    )

    op.create_table(
        "user_roles",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("rol_id", UUID, sa.ForeignKey("roles.id"), nullable=False),
        sa.UniqueConstraint("user_id", "rol_id", name="uq_user_rol"),
    )

    # Seed roles
    roles_table = table(
        "roles",
        column("id", UUID),
        column("codigo", sa.String),
        column("nombre", sa.String),
        column("descripcion", sa.Text),
    )

    # We use gen_random_uuid() for ids, then query them back for perm assignments
    for codigo, info in SEED_ROLES.items():
        op.execute(
            roles_table.insert().values(
                codigo=codigo,
                nombre=info["nombre"],
                descripcion=info["descripcion"],
            )
        )

    # Collect all unique permission codes from all roles
    all_perm_cods: set[str] = set()
    for perms in SEED_ROLE_PERMS.values():
        all_perm_cods.update(perms)

    # Seed permissions
    permisos_table = table(
        "permisos",
        column("id", UUID),
        column("codigo", sa.String),
        column("nombre", sa.String),
        column("descripcion", sa.Text),
        column("modulo", sa.String),
        column("propio", sa.Boolean),
    )

    for codigo in sorted(all_perm_cods):
        modulo = codigo.split(":", 1)[0]
        propio = "(propio)" in codigo
        op.execute(
            permisos_table.insert().values(
                codigo=codigo,
                nombre=_get_perm_nombre(codigo),
                descripcion=PERMISO_DESCRIPTIONS.get(codigo),
                modulo=modulo,
                propio=propio,
            )
        )

    # Seed RolPermiso associations
    rp_table = table(
        "rol_permisos",
        column("id", UUID),
        column("rol_id", UUID),
        column("permiso_id", UUID),
    )

    # Get the generated UUIDs from the DB
    conn = op.get_bind()

    for rol_codigo, perm_cods in SEED_ROLE_PERMS.items():
        rol_row = conn.execute(
            sa.text("SELECT id FROM roles WHERE codigo = :codigo"),
            {"codigo": rol_codigo},
        ).fetchone()
        if rol_row is None:
            continue
        rol_uuid = rol_row[0]

        for perm_codigo in perm_cods:
            perm_row = conn.execute(
                sa.text("SELECT id FROM permisos WHERE codigo = :codigo"),
                {"codigo": perm_codigo},
            ).fetchone()
            if perm_row is None:
                continue
            perm_uuid = perm_row[0]

            op.execute(
                rp_table.insert().values(
                    rol_id=rol_uuid,
                    permiso_id=perm_uuid,
                )
            )


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("rol_permisos")
    op.drop_table("permisos")
    op.drop_table("roles")
