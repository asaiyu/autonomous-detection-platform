from __future__ import annotations

from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RuleCreateRequest(BaseModel):
    mode: Literal["proposal", "ruleset"] = "proposal"
    ruleset_id: str = "default"
    ruleset_note: Optional[str] = None
    title: str
    rule_id: str
    rule_version: int = 1
    rule_yaml: str
    rationale: str
    proposal_status: str = "pending"
    evaluation_id: Optional[UUID] = None
    source_event_id: Optional[UUID] = None
    created_by: str = "manual"
    references_json: Dict[str, Any] = Field(default_factory=dict)
    risk_notes: Optional[str] = None


class RuleCreateResponse(BaseModel):
    proposal_id: Optional[str] = None
    ruleset_id: Optional[str] = None
    status: str
