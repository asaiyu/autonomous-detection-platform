from __future__ import annotations

import json
from typing import Any
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.logging import get_correlation_id
from app.db.session import get_db
from app.models.event import Event
from app.schemas.ingest import (
    BulkIngestError,
    BulkIngestResponse,
    IngestEventRequest,
    IngestEventResponse,
)
from app.services.event_normalization import normalize_event

router = APIRouter()


@router.post("/event", response_model=IngestEventResponse, status_code=status.HTTP_201_CREATED)
def ingest_event(payload: IngestEventRequest, db: Session = Depends(get_db)) -> IngestEventResponse:
    event = _persist_event(payload=payload, db=db)
    db.commit()
    db.refresh(event)

    return IngestEventResponse(
        event_id=str(event.id),
        source_type=event.source,
        timestamp=str(event.canonical_event_json.get("timestamp")),
        canonical_event=event.canonical_event_json,
    )


@router.post("/bulk", response_model=BulkIngestResponse)
async def ingest_bulk(request: Request, db: Session = Depends(get_db)) -> BulkIngestResponse:
    raw_body = (await request.body()).decode("utf-8")
    lines = [line for line in raw_body.splitlines() if line.strip()]
    if not lines:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty NDJSON payload")

    ingested = 0
    errors: list[BulkIngestError] = []

    for index, line in enumerate(lines, start=1):
        try:
            payload = IngestEventRequest.model_validate_json(line)
            _persist_event(payload=payload, db=db)
            db.commit()
            ingested += 1
        except json.JSONDecodeError as exc:
            db.rollback()
            errors.append(BulkIngestError(line_number=index, error=f"invalid JSON: {exc.msg}"))
        except ValidationError as exc:
            db.rollback()
            errors.append(BulkIngestError(line_number=index, error=str(exc)))
        except Exception as exc:  # pragma: no cover - defensive catch for bulk processing
            db.rollback()
            errors.append(BulkIngestError(line_number=index, error=str(exc)))

    return BulkIngestResponse(ingested=ingested, error_count=len(errors), errors=errors)


def _persist_event(payload: IngestEventRequest, db: Session) -> Event:
    normalized = normalize_event(
        source_type=payload.source_type,
        raw_event=payload.raw_event,
        timestamp=payload.timestamp,
    )
    event_type = _get_event_type(normalized.canonical_event)

    event = Event(
        id=normalized.event_id,
        source=payload.source_type,
        event_type=event_type,
        payload=normalized.canonical_event,
        raw_event_json=payload.raw_event,
        canonical_event_json=normalized.canonical_event,
        occurred_at=normalized.occurred_at,
        correlation_id=get_correlation_id(),
    )
    db.add(event)
    return event


def _get_event_type(canonical_event: dict[str, Any]) -> Optional[str]:
    event = canonical_event.get("event")
    if isinstance(event, dict):
        event_type = event.get("type")
        if isinstance(event_type, str):
            return event_type
    return None
