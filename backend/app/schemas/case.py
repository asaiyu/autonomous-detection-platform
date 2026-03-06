from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class TriageOutput(BaseModel):
    triage_summary: str
    likely_technique: Optional[str]
    recommended_actions: list[str] = Field(default_factory=list)
    case_notes: str
    citations: list[str] = Field(default_factory=list)


class CaseResponse(BaseModel):
    case_id: str
    alert_id: str
    notes_markdown: Optional[str]
    triage_json: Optional[dict[str, Any]]
    created_at: str
    updated_at: str


class CaseListResponse(BaseModel):
    count: int
    items: list[CaseResponse] = Field(default_factory=list)


class TriageRequest(BaseModel):
    analyst_notes: Optional[str] = None


class CaseUpdateRequest(BaseModel):
    notes_markdown: Optional[str] = None
    triage_json: Optional[dict[str, Any]] = None
