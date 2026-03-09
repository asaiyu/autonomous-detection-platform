from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SearchEventsToolRequest(BaseModel):
    query: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    limit: int = 100


class SearchAlertsToolRequest(BaseModel):
    query: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    limit: int = 100


class GetAlertContextToolRequest(BaseModel):
    alert_id: UUID


class RunReplayToolRequest(BaseModel):
    dataset_id: str
    ruleset_id: str
    mode: str


class CreateRuleProposalToolRequest(BaseModel):
    title: str
    rule_id: str
    rule_version: int = 1
    rule_yaml: str
    rationale: str
    created_by: str = "mcp"
    references_json: dict[str, Any] = Field(default_factory=dict)
