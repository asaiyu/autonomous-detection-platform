"""rename key columns to match docs naming

Revision ID: 0005_doc_column_renames
Revises: 0004_doc_alignment_columns
Create Date: 2026-03-06 02:15:00
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_doc_column_renames"
down_revision: Union[str, None] = "0004_doc_alignment_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("events", "id", new_column_name="event_id")
    op.alter_column("events", "source", new_column_name="source_type")
    op.alter_column("events", "occurred_at", new_column_name="timestamp")

    op.alter_column("alerts", "id", new_column_name="alert_id")
    op.alter_column("alerts", "alert_type", new_column_name="type")

    op.alter_column("attack_runs", "id", new_column_name="run_id")
    op.alter_column("findings", "id", new_column_name="finding_id")
    op.alter_column("coverage_evaluations", "id", new_column_name="evaluation_id")
    op.alter_column("rule_proposals", "id", new_column_name="proposal_id")
    op.alter_column("replay_validations", "id", new_column_name="validation_id")
    op.alter_column("coverage_snapshots", "id", new_column_name="snapshot_id")


def downgrade() -> None:
    op.alter_column("coverage_snapshots", "snapshot_id", new_column_name="id")
    op.alter_column("replay_validations", "validation_id", new_column_name="id")
    op.alter_column("rule_proposals", "proposal_id", new_column_name="id")
    op.alter_column("coverage_evaluations", "evaluation_id", new_column_name="id")
    op.alter_column("findings", "finding_id", new_column_name="id")
    op.alter_column("attack_runs", "run_id", new_column_name="id")

    op.alter_column("alerts", "type", new_column_name="alert_type")
    op.alter_column("alerts", "alert_id", new_column_name="id")

    op.alter_column("events", "timestamp", new_column_name="occurred_at")
    op.alter_column("events", "source_type", new_column_name="source")
    op.alter_column("events", "event_id", new_column_name="id")
