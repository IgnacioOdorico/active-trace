"""grant auditoria:ver a FINANZAS, segun knowledge-base/03_actores_y_roles.md

Revision ID: 020
Revises: 019
Create Date: 2026-06-19

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "020"
down_revision: str | None = "019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO rol_permisos (id, rol_id, permiso_id)
            SELECT gen_random_uuid(), r.id, p.id
            FROM roles r, permisos p
            WHERE r.codigo = 'FINANZAS' AND p.codigo = 'auditoria:ver'
            ON CONFLICT DO NOTHING
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM rol_permisos
            WHERE rol_id = (SELECT id FROM roles WHERE codigo = 'FINANZAS')
              AND permiso_id = (SELECT id FROM permisos WHERE codigo = 'auditoria:ver')
            """
        )
    )
