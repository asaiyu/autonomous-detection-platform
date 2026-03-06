from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.coverage_snapshot import CoverageSnapshot
from app.schemas.coverage import CoverageDiffResponse, CoverageSnapshotListResponse, CoverageSnapshotResponse

router = APIRouter()


@router.get("/snapshots", response_model=CoverageSnapshotListResponse)
def list_coverage_snapshots(
    dataset_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> CoverageSnapshotListResponse:
    db_query = db.query(CoverageSnapshot)
    if dataset_id:
        db_query = db_query.filter(CoverageSnapshot.dataset_id == dataset_id)

    rows = db_query.order_by(CoverageSnapshot.created_at.desc()).limit(limit).all()
    items = [_to_snapshot_response(row) for row in rows]
    return CoverageSnapshotListResponse(count=len(items), items=items)


@router.get("/diff", response_model=CoverageDiffResponse)
def coverage_diff(
    dataset_id: str = Query(...),
    from_ruleset: str = Query(...),
    to_ruleset: str = Query(...),
    db: Session = Depends(get_db),
) -> CoverageDiffResponse:
    from_snapshot = (
        db.query(CoverageSnapshot)
        .filter(
            CoverageSnapshot.dataset_id == dataset_id,
            CoverageSnapshot.ruleset_id_text == from_ruleset,
        )
        .order_by(CoverageSnapshot.created_at.desc())
        .first()
    )
    to_snapshot = (
        db.query(CoverageSnapshot)
        .filter(
            CoverageSnapshot.dataset_id == dataset_id,
            CoverageSnapshot.ruleset_id_text == to_ruleset,
        )
        .order_by(CoverageSnapshot.created_at.desc())
        .first()
    )

    if from_snapshot is None or to_snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="coverage snapshots not found for requested dataset/rulesets",
        )

    from_rate = _extract_coverage_rate(from_snapshot.metrics_json, from_snapshot.coverage_percent)
    to_rate = _extract_coverage_rate(to_snapshot.metrics_json, to_snapshot.coverage_percent)
    delta = None if from_rate is None or to_rate is None else round(to_rate - from_rate, 4)

    return CoverageDiffResponse(
        dataset_id=dataset_id,
        from_ruleset=from_ruleset,
        to_ruleset=to_ruleset,
        from_coverage_rate=from_rate,
        to_coverage_rate=to_rate,
        delta=delta,
    )


def _to_snapshot_response(snapshot: CoverageSnapshot) -> CoverageSnapshotResponse:
    return CoverageSnapshotResponse(
        snapshot_id=str(snapshot.id),
        dataset_id=snapshot.dataset_id,
        ruleset_id=snapshot.ruleset_id_text,
        computed_at=_datetime_to_utc_iso(snapshot.computed_at or snapshot.snapshot_at),
        metrics_json=snapshot.metrics_json or snapshot.summary or {},
    )


def _extract_coverage_rate(
    metrics_json: Optional[dict[str, Any]],
    coverage_percent: Optional[float],
) -> Optional[float]:
    if isinstance(metrics_json, dict):
        value = metrics_json.get("coverage_rate")
        if isinstance(value, (float, int)):
            return round(float(value), 4)
    if coverage_percent is None:
        return None
    return round(float(coverage_percent), 4)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _datetime_to_utc_iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")
