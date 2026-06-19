"""grant calificaciones:importar y padron:importar a COORDINADOR

FL-02 (importacion de calificaciones) y FL-03 paso 8 (importacion del
padron inicial, knowledge-base/07_flujos_principales.md) documentan al
COORDINADOR ejecutando ambas acciones, pero solo tenia calificaciones:ver
y padron:ver (lectura).

Ninguno de los dos codigos existia en el catalogo `permisos`: viven
hardcodeados en require_permission() de calificaciones.py/umbral.py/
padron.py, pero ninguna migracion anterior creo la fila (PROFESOR los
cubre via el wildcard calificaciones:*, que si tiene fila propia). Hay
que crear el permiso antes de poder otorgarlo.

Revision ID: 021
Revises: 020
Create Date: 2026-06-19

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "021"
down_revision: str | None = "020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PERMISOS = {
    "calificaciones:importar": "Importar calificaciones",
    "padron:importar": "Importar padron de alumnos",
}


def upgrade() -> None:
    conn = op.get_bind()
    for codigo, descripcion in _PERMISOS.items():
        modulo = codigo.split(":", 1)[0]
        conn.execute(
            sa.text(
                """
                INSERT INTO permisos (id, codigo, nombre, descripcion, modulo, propio)
                VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, :modulo, false)
                ON CONFLICT (codigo) DO NOTHING
                """
            ),
            {"codigo": codigo, "nombre": descripcion, "descripcion": descripcion, "modulo": modulo},
        )
        conn.execute(
            sa.text(
                """
                INSERT INTO rol_permisos (id, rol_id, permiso_id)
                SELECT gen_random_uuid(), r.id, p.id
                FROM roles r, permisos p
                WHERE r.codigo = 'COORDINADOR' AND p.codigo = :codigo
                ON CONFLICT DO NOTHING
                """
            ),
            {"codigo": codigo},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for codigo in _PERMISOS:
        conn.execute(
            sa.text(
                """
                DELETE FROM rol_permisos
                WHERE rol_id = (SELECT id FROM roles WHERE codigo = 'COORDINADOR')
                  AND permiso_id = (SELECT id FROM permisos WHERE codigo = :codigo)
                """
            ),
            {"codigo": codigo},
        )
