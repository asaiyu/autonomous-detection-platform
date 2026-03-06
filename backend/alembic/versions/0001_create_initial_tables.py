"""create initial tables

Revision ID: 0001_create_initial_tables
Revises: 
Create Date: 2026-03-05 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_create_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "attack_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "rulesets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("rules", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "rule_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "replay_validations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attack_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["attack_run_id"], ["attack_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "coverage_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ruleset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("coverage_percent", sa.Float(), nullable=False),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ruleset_id"], ["rulesets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "coverage_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attack_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ruleset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scenario", sa.String(length=128), nullable=False),
        sa.Column("result", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["attack_run_id"], ["attack_runs.id"]),
        sa.ForeignKeyConstraint(["ruleset_id"], ["rulesets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attack_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("alert_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("finding_type", sa.String(length=64), nullable=False),
        sa.Column("detail", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"]),
        sa.ForeignKeyConstraint(["attack_run_id"], ["attack_runs.id"]),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("findings")
    op.drop_table("coverage_evaluations")
    op.drop_table("coverage_snapshots")
    op.drop_table("replay_validations")
    op.drop_table("rule_proposals")
    op.drop_table("alerts")
    op.drop_table("rulesets")
    op.drop_table("attack_runs")
    op.drop_table("events")
