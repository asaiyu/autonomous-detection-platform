"""add alert evidence and rule metadata columns

Revision ID: 0003_alert_evidence
Revises: 0002_event_json_cols
Create Date: 2026-03-06 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_alert_evidence"
down_revision: Union[str, None] = "0002_event_json_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("rule_id", sa.String(length=128), nullable=True))
    op.add_column("alerts", sa.Column("rule_version", sa.Integer(), nullable=True))
    op.add_column("alerts", sa.Column("category", sa.String(length=64), nullable=True))
    op.add_column("alerts", sa.Column("alert_type", sa.String(length=64), nullable=True))
    op.add_column("alerts", sa.Column("confidence", sa.Float(), nullable=True))
    op.add_column(
        "alerts",
        sa.Column(
            "evidence_event_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "alerts",
        sa.Column(
            "evidence_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("alerts", "evidence_json")
    op.drop_column("alerts", "evidence_event_ids")
    op.drop_column("alerts", "confidence")
    op.drop_column("alerts", "alert_type")
    op.drop_column("alerts", "category")
    op.drop_column("alerts", "rule_version")
    op.drop_column("alerts", "rule_id")
