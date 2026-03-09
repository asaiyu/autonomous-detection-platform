"""add raw and canonical event json columns

Revision ID: 0002_event_json_cols
Revises: 0001_create_initial_tables
Create Date: 2026-03-06 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_event_json_cols"
down_revision: Union[str, None] = "0001_create_initial_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "events",
        sa.Column("raw_event_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "events",
        sa.Column("canonical_event_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.execute("UPDATE events SET raw_event_json = payload WHERE raw_event_json IS NULL")
    op.execute("UPDATE events SET canonical_event_json = payload WHERE canonical_event_json IS NULL")

    op.alter_column("events", "raw_event_json", nullable=False)
    op.alter_column("events", "canonical_event_json", nullable=False)
    op.alter_column("events", "event_type", existing_type=sa.String(length=128), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE events SET event_type = '' WHERE event_type IS NULL")
    op.alter_column("events", "event_type", existing_type=sa.String(length=128), nullable=False)
    op.drop_column("events", "canonical_event_json")
    op.drop_column("events", "raw_event_json")
