from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    alert_id: str
    event_id: Optional[str]
    rule_id: Optional[str]
    rule_version: Optional[int]
    severity: str
    title: str
    category: Optional[str]
    type: Optional[str]
    status: str
    confidence: Optional[float]
    description: Optional[str]
    evidence_event_ids: list[str] = Field(default_factory=list)
    evidence_json: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    metadata: Optional[dict[str, Any]] = None
    created_at: str


class AlertListResponse(BaseModel):
    count: int
    items: list[AlertResponse] = Field(default_factory=list)


class AlertEvidenceResponse(BaseModel):
    alert_id: str
    evidence_event_ids: list[str] = Field(default_factory=list)
    evidence_json: dict[str, Any] = Field(default_factory=dict)
