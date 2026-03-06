from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class RunResponse(BaseModel):
    run_id: str
    name: str
    attack_source: Optional[str]
    dataset_id: Optional[str]
    target: Optional[str]
    status: str
    summary: Optional[str]
    config_json: Optional[dict[str, Any]]
    config_hash: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    created_at: str


class RunListResponse(BaseModel):
    count: int
    items: list[RunResponse] = Field(default_factory=list)


class FindingResponse(BaseModel):
    finding_id: str
    run_id: Optional[str]
    finding_type: str
    title: Optional[str]
    severity: Optional[str]
    technique: Optional[str]
    occurred_at: Optional[str]
    entrypoint_json: Optional[dict[str, Any]]
    proof_json: Optional[dict[str, Any]]
    tags_json: Optional[dict[str, Any]]


class FindingListResponse(BaseModel):
    count: int
    items: list[FindingResponse] = Field(default_factory=list)
