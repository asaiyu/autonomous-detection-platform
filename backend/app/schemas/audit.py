from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class AuditCoverageSnapshotResponse(BaseModel):
    dataset_id: str
    ruleset_id: str
    snapshot_id: str
    metrics_json: dict[str, Any] = Field(default_factory=dict)
    top_gaps: list[dict[str, Any]] = Field(default_factory=list)
    rules_merged_count: int
    rules_validated_count: int
    generated_at: str


class AuditCoverageDiffResponse(BaseModel):
    dataset_id: str
    from_ruleset: str
    to_ruleset: str
    coverage_rate_delta: Optional[float]
    gaps_closed_count: Optional[int]
    rules_responsible: list[str] = Field(default_factory=list)
    replay_validation_refs: list[str] = Field(default_factory=list)
    generated_at: str


class AuditRunReportResponse(BaseModel):
    run_id: str
    run_metadata: dict[str, Any] = Field(default_factory=dict)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    coverage_evaluations: list[dict[str, Any]] = Field(default_factory=list)
    rule_proposals: list[dict[str, Any]] = Field(default_factory=list)
    replay_validations: list[dict[str, Any]] = Field(default_factory=list)
    generated_at: str
