from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Text, cast
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.event import Event
from app.schemas.event import EventListResponse, EventResponse

router = APIRouter()


@router.get("", response_model=EventListResponse)
def list_events(
    start_timestamp: Optional[datetime] = Query(None),
    end_timestamp: Optional[datetime] = Query(None),
    source_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> EventListResponse:
    query = db.query(Event)

    if start_timestamp is not None:
        query = query.filter(Event.occurred_at >= _ensure_utc(start_timestamp))
    if end_timestamp is not None:
        query = query.filter(Event.occurred_at <= _ensure_utc(end_timestamp))
    if source_type:
        query = query.filter(Event.source == source_type)
    if q:
        query = query.filter(cast(Event.canonical_event_json, Text).ilike(f"%{q}%"))

    rows = query.order_by(Event.occurred_at.desc()).limit(limit).all()
    items = [_to_event_response(row) for row in rows]
    return EventListResponse(count=len(items), items=items)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: UUID, db: Session = Depends(get_db)) -> EventResponse:
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")
    return _to_event_response(event)


def _to_event_response(event: Event) -> EventResponse:
    return EventResponse(
        event_id=str(event.id),
        source_type=event.source,
        event_type=event.event_type,
        timestamp=_datetime_to_utc_iso(event.occurred_at),
        raw_event_json=event.raw_event_json,
        canonical_event_json=event.canonical_event_json,
        correlation_id=event.correlation_id,
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _datetime_to_utc_iso(value: datetime) -> str:
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")
