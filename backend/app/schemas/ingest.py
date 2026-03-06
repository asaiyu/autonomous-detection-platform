from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

SourceType = Literal["dns", "firewall", "windows", "macos", "http", "application"]


class IngestEventRequest(BaseModel):
    source_type: SourceType
    raw_event: dict[str, Any]
    timestamp: Optional[str] = None


class IngestEventResponse(BaseModel):
    event_id: str
    source_type: str
    timestamp: str
    canonical_event: dict[str, Any]


class BulkIngestError(BaseModel):
    line_number: int
    error: str


class BulkIngestResponse(BaseModel):
    ingested: int
    error_count: int
    errors: list[BulkIngestError] = Field(default_factory=list)
