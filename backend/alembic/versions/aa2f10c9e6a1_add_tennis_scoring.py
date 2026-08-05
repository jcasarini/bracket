"""add tennis scoring

Revision ID: aa2f10c9e6a1
Revises: c1ab44651e79
Create Date: 2026-08-04 12:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str | None = "aa2f10c9e6a1"
down_revision: str | None = "c1ab44651e79"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "tournaments",
        sa.Column(
            "scoring_type",
            sa.Enum(
                "STANDARD",
                "TENNIS",
                name="scoring_type",
            ),
            nullable=False,
            server_default="STANDARD",
        ),
    )
    op.add_column(
        "tournaments",
        sa.Column("sets_to_win", sa.Integer(), nullable=False, server_default="2"),
    )
    op.add_column("matches", sa.Column("scores", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("matches", "scores")
    op.drop_column("tournaments", "sets_to_win")
    op.drop_column("tournaments", "scoring_type")
