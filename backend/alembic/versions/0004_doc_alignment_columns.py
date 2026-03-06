"""add doc alignment columns for coverage and run APIs

Revision ID: 0004_doc_alignment_columns
Revises: 0003_alert_evidence
Create Date: 2026-03-06 01:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0004_doc_alignment_columns"
down_revision: Union[str, None] = "0003_alert_evidence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("events", sa.Column("dataset_id", sa.String(length=128), nullable=True))
    op.add_column("events", sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True))

    op.add_column(
        "alerts",
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column("attack_runs", sa.Column("attack_source", sa.String(length=128), nullable=True))
    op.add_column("attack_runs", sa.Column("dataset_id", sa.String(length=128), nullable=True))
    op.add_column("attack_runs", sa.Column("target", sa.String(length=256), nullable=True))
    op.add_column("attack_runs", sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("attack_runs", sa.Column("config_hash", sa.String(length=128), nullable=True))
    op.add_column("attack_runs", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("attack_runs", sa.Column("start_time", sa.DateTime(timezone=True), nullable=True))
    op.add_column("attack_runs", sa.Column("end_time", sa.DateTime(timezone=True), nullable=True))

    op.add_column("findings", sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_findings_run_id", "findings", "attack_runs", ["run_id"], ["id"])
    op.add_column("findings", sa.Column("title", sa.String(length=256), nullable=True))
    op.add_column("findings", sa.Column("severity", sa.String(length=32), nullable=True))
    op.add_column("findings", sa.Column("technique", sa.String(length=128), nullable=True))
    op.add_column("findings", sa.Column("entrypoint_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("findings", sa.Column("proof_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("findings", sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("findings", sa.Column("tags_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("findings", sa.Column("notes", sa.Text(), nullable=True))

    op.add_column("coverage_evaluations", sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_coverage_evaluations_run_id", "coverage_evaluations", "attack_runs", ["run_id"], ["id"])
    op.add_column("coverage_evaluations", sa.Column("finding_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_coverage_evaluations_finding_id",
        "coverage_evaluations",
        "findings",
        ["finding_id"],
        ["id"],
    )
    op.add_column("coverage_evaluations", sa.Column("coverage_state", sa.String(length=64), nullable=True))
    op.add_column("coverage_evaluations", sa.Column("window_start", sa.DateTime(timezone=True), nullable=True))
    op.add_column("coverage_evaluations", sa.Column("window_end", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "coverage_evaluations",
        sa.Column("related_event_ids_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "coverage_evaluations",
        sa.Column("related_alert_ids_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "coverage_evaluations",
        sa.Column("missing_telemetry_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("coverage_evaluations", sa.Column("notes", sa.Text(), nullable=True))

    op.add_column("rule_proposals", sa.Column("evaluation_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_rule_proposals_evaluation_id",
        "rule_proposals",
        "coverage_evaluations",
        ["evaluation_id"],
        ["id"],
    )
    op.add_column("rule_proposals", sa.Column("rule_id", sa.String(length=128), nullable=True))
    op.add_column("rule_proposals", sa.Column("rule_version", sa.Integer(), nullable=True))
    op.add_column("rule_proposals", sa.Column("proposal_status", sa.String(length=32), nullable=True))
    op.add_column("rule_proposals", sa.Column("rule_yaml", sa.Text(), nullable=True))
    op.add_column("rule_proposals", sa.Column("created_by", sa.String(length=128), nullable=True))
    op.add_column("rule_proposals", sa.Column("references_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("rule_proposals", sa.Column("risk_notes", sa.Text(), nullable=True))

    op.alter_column("replay_validations", "attack_run_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.add_column("replay_validations", sa.Column("proposal_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_replay_validations_proposal_id", "replay_validations", "rule_proposals", ["proposal_id"], ["id"])
    op.add_column("replay_validations", sa.Column("attack_dataset_id", sa.String(length=128), nullable=True))
    op.add_column("replay_validations", sa.Column("baseline_dataset_id", sa.String(length=128), nullable=True))
    op.add_column("replay_validations", sa.Column("replay_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("replay_validations", sa.Column("replay_finished_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("replay_validations", sa.Column("results_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("replay_validations", sa.Column("verdict", sa.String(length=16), nullable=True))
    op.add_column("replay_validations", sa.Column("report", sa.Text(), nullable=True))

    op.add_column("rulesets", sa.Column("ruleset_id", sa.String(length=128), nullable=True))
    op.create_unique_constraint("uq_rulesets_ruleset_id", "rulesets", ["ruleset_id"])
    op.add_column("rulesets", sa.Column("note", sa.Text(), nullable=True))

    op.add_column("coverage_snapshots", sa.Column("dataset_id", sa.String(length=128), nullable=True))
    op.add_column("coverage_snapshots", sa.Column("ruleset_id_text", sa.String(length=128), nullable=True))
    op.add_column("coverage_snapshots", sa.Column("computed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("coverage_snapshots", sa.Column("metrics_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("coverage_snapshots", "metrics_json")
    op.drop_column("coverage_snapshots", "computed_at")
    op.drop_column("coverage_snapshots", "ruleset_id_text")
    op.drop_column("coverage_snapshots", "dataset_id")

    op.drop_column("rulesets", "note")
    op.drop_constraint("uq_rulesets_ruleset_id", "rulesets", type_="unique")
    op.drop_column("rulesets", "ruleset_id")

    op.drop_column("replay_validations", "report")
    op.drop_column("replay_validations", "verdict")
    op.drop_column("replay_validations", "results_json")
    op.drop_column("replay_validations", "replay_finished_at")
    op.drop_column("replay_validations", "replay_started_at")
    op.drop_column("replay_validations", "baseline_dataset_id")
    op.drop_column("replay_validations", "attack_dataset_id")
    op.drop_constraint("fk_replay_validations_proposal_id", "replay_validations", type_="foreignkey")
    op.drop_column("replay_validations", "proposal_id")
    op.alter_column("replay_validations", "attack_run_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)

    op.drop_column("rule_proposals", "risk_notes")
    op.drop_column("rule_proposals", "references_json")
    op.drop_column("rule_proposals", "created_by")
    op.drop_column("rule_proposals", "rule_yaml")
    op.drop_column("rule_proposals", "proposal_status")
    op.drop_column("rule_proposals", "rule_version")
    op.drop_column("rule_proposals", "rule_id")
    op.drop_constraint("fk_rule_proposals_evaluation_id", "rule_proposals", type_="foreignkey")
    op.drop_column("rule_proposals", "evaluation_id")

    op.drop_column("coverage_evaluations", "notes")
    op.drop_column("coverage_evaluations", "missing_telemetry_json")
    op.drop_column("coverage_evaluations", "related_alert_ids_json")
    op.drop_column("coverage_evaluations", "related_event_ids_json")
    op.drop_column("coverage_evaluations", "window_end")
    op.drop_column("coverage_evaluations", "window_start")
    op.drop_column("coverage_evaluations", "coverage_state")
    op.drop_constraint("fk_coverage_evaluations_finding_id", "coverage_evaluations", type_="foreignkey")
    op.drop_column("coverage_evaluations", "finding_id")
    op.drop_constraint("fk_coverage_evaluations_run_id", "coverage_evaluations", type_="foreignkey")
    op.drop_column("coverage_evaluations", "run_id")

    op.drop_column("findings", "notes")
    op.drop_column("findings", "tags_json")
    op.drop_column("findings", "occurred_at")
    op.drop_column("findings", "proof_json")
    op.drop_column("findings", "entrypoint_json")
    op.drop_column("findings", "technique")
    op.drop_column("findings", "severity")
    op.drop_column("findings", "title")
    op.drop_constraint("fk_findings_run_id", "findings", type_="foreignkey")
    op.drop_column("findings", "run_id")

    op.drop_column("attack_runs", "end_time")
    op.drop_column("attack_runs", "start_time")
    op.drop_column("attack_runs", "summary")
    op.drop_column("attack_runs", "config_hash")
    op.drop_column("attack_runs", "config_json")
    op.drop_column("attack_runs", "target")
    op.drop_column("attack_runs", "dataset_id")
    op.drop_column("attack_runs", "attack_source")

    op.drop_column("alerts", "tags")

    op.drop_column("events", "run_id")
    op.drop_column("events", "dataset_id")
