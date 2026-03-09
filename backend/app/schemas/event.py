from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    event_id: str
    source_type: str
    event_type: Optional[str]
    timestamp: str
    raw_event_json: dict[str, Any]
    canonical_event_json: dict[str, Any]
    correlation_id: Optional[str]


class EventListResponse(BaseModel):
    count: int
    items: list[EventResponse] = Field(default_factory=list)
