from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attack_run import AttackRun
from app.models.finding import Finding
from app.schemas.run import FindingListResponse, FindingResponse, RunListResponse, RunResponse

router = APIRouter()


@router.get("", response_model=RunListResponse)
def list_runs(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> RunListResponse:
    rows = db.query(AttackRun).order_by(AttackRun.created_at.desc()).limit(limit).all()
    items = [_to_run_response(row) for row in rows]
    return RunListResponse(count=len(items), items=items)


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: UUID, db: Session = Depends(get_db)) -> RunResponse:
    run = db.query(AttackRun).filter(AttackRun.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="run not found")
    return _to_run_response(run)


@router.get("/{run_id}/findings", response_model=FindingListResponse)
def get_run_findings(
    run_id: UUID,
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> FindingListResponse:
    rows = (
        db.query(Finding)
        .filter(or_(Finding.attack_run_id == run_id, Finding.run_id == run_id))
        .order_by(Finding.created_at.desc())
        .limit(limit)
        .all()
    )
    items = [_to_finding_response(row) for row in rows]
    return FindingListResponse(count=len(items), items=items)


def _to_run_response(run: AttackRun) -> RunResponse:
    return RunResponse(
        run_id=str(run.id),
        name=run.name,
        attack_source=run.attack_source,
        dataset_id=run.dataset_id,
        target=run.target,
        status=run.status,
        summary=run.summary or run.notes,
        config_json=run.config_json,
        config_hash=run.config_hash,
        start_time=_datetime_to_utc_iso(run.start_time or run.started_at),
        end_time=_datetime_to_utc_iso(run.end_time or run.finished_at),
        created_at=_datetime_to_utc_iso(run.created_at) or "",
    )


def _to_finding_response(finding: Finding) -> FindingResponse:
    return FindingResponse(
        finding_id=str(finding.id),
        run_id=str(finding.run_id or finding.attack_run_id) if (finding.run_id or finding.attack_run_id) else None,
        finding_type=finding.finding_type,
        title=finding.title,
        severity=finding.severity,
        technique=finding.technique,
        occurred_at=_datetime_to_utc_iso(finding.occurred_at),
        entrypoint_json=finding.entrypoint_json,
        proof_json=finding.proof_json,
        tags_json=finding.tags_json,
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _datetime_to_utc_iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")
