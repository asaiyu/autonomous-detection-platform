from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.detection.replay_service import replay_dataset
from app.schemas.replay import ReplayRequest, ReplayResponse

router = APIRouter()


@router.post("", response_model=ReplayResponse)
def replay(request: ReplayRequest, db: Session = Depends(get_db)) -> ReplayResponse:
    try:
        result = replay_dataset(
            dataset_id=request.dataset_id,
            ruleset_id=request.ruleset_id,
            mode=request.mode,
            db=db,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ReplayResponse(
        dataset_id=result.dataset_id,
        ruleset_id=result.ruleset_id,
        mode=result.mode,
        alerts_generated=result.alerts_generated,
        attack_tp_count=result.attack_tp_count,
        baseline_fp_count=result.baseline_fp_count,
        coverage_rate=result.coverage_rate,
        verdict=result.verdict,
        allowed_fp_threshold=result.allowed_fp_threshold,
        sample_alert_ids=result.sample_alert_ids,
        sample_event_ids=result.sample_event_ids,
        started_at=result.started_at,
        finished_at=result.finished_at,
    )
