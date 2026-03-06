from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class CoverageSnapshotResponse(BaseModel):
    snapshot_id: str
    dataset_id: Optional[str]
    ruleset_id: Optional[str]
    computed_at: Optional[str]
    metrics_json: dict[str, Any] = Field(default_factory=dict)


class CoverageSnapshotListResponse(BaseModel):
    count: int
    items: list[CoverageSnapshotResponse] = Field(default_factory=list)


class CoverageDiffResponse(BaseModel):
    dataset_id: str
    from_ruleset: str
    to_ruleset: str
    from_coverage_rate: Optional[float]
    to_coverage_rate: Optional[float]
    delta: Optional[float]
