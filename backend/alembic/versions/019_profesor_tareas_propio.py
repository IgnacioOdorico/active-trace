"""revoke tareas:gestionar (full) from PROFESOR — debe gestionar solo sus tareas propias

Revision ID: 019
Revises: 018
Create Date: 2026-06-19

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "019"
down_revision: str | None = "018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM rol_permisos
            WHERE rol_id = (SELECT id FROM roles WHERE codigo = 'PROFESOR')
              AND permiso_id = (SELECT id FROM permisos WHERE codigo = 'tareas:gestionar')
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO rol_permisos (id, rol_id, permiso_id)
            SELECT gen_random_uuid(), r.id, p.id
            FROM roles r, permisos p
            WHERE r.codigo = 'PROFESOR' AND p.codigo = 'tareas:gestionar'
            ON CONFLICT DO NOTHING
            """
        )
    )
