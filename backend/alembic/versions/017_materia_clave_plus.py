"""add clave_plus to materias (resolución PA-22: categoría de Plus salarial)

Revision ID: 017
Revises: 016
Create Date: 2026-06-18

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "017"
down_revision: str | None = "016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Mapeo fijo materia -> clave de Plus, precargado por el equipo de producto
# (PA-22). No es editable desde la UI de tenant; nuevas materias requieren
# una migración de datos nueva para asignarles clave.
CLAVE_PLUS_POR_CODIGO = {
    "PROG1": "PROG",
    "PROG2": "PROG",
    "BD1": "BD",
    "MAT1": "MAT",
    "ING1": "ING",
}


def upgrade() -> None:
    op.add_column("materias", sa.Column("clave_plus", sa.String(20), nullable=True))

    conn = op.get_bind()
    for codigo, clave in CLAVE_PLUS_POR_CODIGO.items():
        conn.execute(
            sa.text("UPDATE materias SET clave_plus = :clave WHERE codigo = :codigo"),
            {"clave": clave, "codigo": codigo},
        )


def downgrade() -> None:
    op.drop_column("materias", "clave_plus")
