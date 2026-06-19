"""add deleted_at to liquidaciones (soft-delete del borrador al recalcular)

Revision ID: 018
Revises: 017
Create Date: 2026-06-18

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "018"
down_revision: str | None = "017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "liquidaciones",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("liquidaciones", "deleted_at")
