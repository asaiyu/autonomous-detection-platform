from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Text, cast
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertEvidenceResponse, AlertListResponse, AlertResponse

router = APIRouter()


@router.get("", response_model=AlertListResponse)
def list_alerts(
    query: Optional[str] = Query(None),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    q: Optional[str] = Query(None),
    start_timestamp: Optional[datetime] = Query(None),
    end_timestamp: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    text_query = query or q
    start_time = start or start_timestamp
    end_time = end or end_timestamp

    db_query = db.query(Alert)
    if start_time is not None:
        db_query = db_query.filter(Alert.created_at >= _ensure_utc(start_time))
    if end_time is not None:
        db_query = db_query.filter(Alert.created_at <= _ensure_utc(end_time))
    if text_query:
        db_query = db_query.filter(
            cast(Alert.title, Text).ilike(f"%{text_query}%") | cast(Alert.evidence_json, Text).ilike(f"%{text_query}%")
        )

    rows = db_query.order_by(Alert.created_at.desc()).limit(limit).all()
    items = [_to_alert_response(row) for row in rows]
    return AlertListResponse(count=len(items), items=items)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: UUID, db: Session = Depends(get_db)) -> AlertResponse:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="alert not found")
    return _to_alert_response(alert)


@router.get("/{alert_id}/evidence", response_model=AlertEvidenceResponse)
def get_alert_evidence(alert_id: UUID, db: Session = Depends(get_db)) -> AlertEvidenceResponse:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="alert not found")
    return AlertEvidenceResponse(
        alert_id=str(alert.id),
        evidence_event_ids=alert.evidence_event_ids or [],
        evidence_json=alert.evidence_json or {},
    )


def _to_alert_response(alert: Alert) -> AlertResponse:
    return AlertResponse(
        alert_id=str(alert.id),
        event_id=str(alert.event_id) if alert.event_id else None,
        rule_id=alert.rule_id,
        rule_version=alert.rule_version,
        severity=alert.severity,
        title=alert.title,
        category=alert.category,
        type=alert.alert_type,
        status=alert.status,
        confidence=alert.confidence,
        description=alert.description,
        evidence_event_ids=alert.evidence_event_ids or [],
        evidence_json=alert.evidence_json or {},
        tags=alert.tags or [],
        metadata=alert.extra,
        created_at=_datetime_to_utc_iso(alert.created_at),
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _datetime_to_utc_iso(value: datetime) -> str:
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")
