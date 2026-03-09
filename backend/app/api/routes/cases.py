from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.case import CaseRecord
from app.schemas.case import CaseListResponse, CaseResponse, CaseUpdateRequest

router = APIRouter()


@router.get("", response_model=CaseListResponse)
def list_cases(
    alert_id: Optional[UUID] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> CaseListResponse:
    db_query = db.query(CaseRecord)
    if alert_id is not None:
        db_query = db_query.filter(CaseRecord.alert_id == alert_id)

    rows = db_query.order_by(CaseRecord.updated_at.desc()).limit(limit).all()
    items = [_to_case_response(row) for row in rows]
    return CaseListResponse(count=len(items), items=items)


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: UUID, db: Session = Depends(get_db)) -> CaseResponse:
    case = db.query(CaseRecord).filter(CaseRecord.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="case not found")
    return _to_case_response(case)


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(case_id: UUID, payload: CaseUpdateRequest, db: Session = Depends(get_db)) -> CaseResponse:
    case = db.query(CaseRecord).filter(CaseRecord.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="case not found")

    if payload.notes_markdown is not None:
        case.notes_markdown = payload.notes_markdown
    if payload.triage_json is not None:
        case.triage_json = payload.triage_json

    db.commit()
    db.refresh(case)
    return _to_case_response(case)


def _to_case_response(case: CaseRecord) -> CaseResponse:
    return CaseResponse(
        case_id=str(case.id),
        alert_id=str(case.alert_id),
        notes_markdown=case.notes_markdown,
        triage_json=case.triage_json,
        created_at=_datetime_to_utc_iso(case.created_at),
        updated_at=_datetime_to_utc_iso(case.updated_at),
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _datetime_to_utc_iso(value: datetime) -> str:
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")
