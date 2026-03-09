from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attack_run import AttackRun
from app.models.coverage_evaluation import CoverageEvaluation
from app.models.coverage_snapshot import CoverageSnapshot
from app.models.finding import Finding
from app.models.replay_validation import ReplayValidation
from app.models.rule_proposal import RuleProposal
from app.schemas.audit import (
    AuditCoverageDiffResponse,
    AuditCoverageSnapshotResponse,
    AuditRunReportResponse,
)

router = APIRouter()


@router.get("/coverage/snapshot")
def export_coverage_snapshot(
    dataset_id: str = Query(...),
    ruleset_id: str = Query(...),
    format: str = Query("json"),
    db: Session = Depends(get_db),
) -> Any:
    snapshot = (
        db.query(CoverageSnapshot)
        .filter(
            CoverageSnapshot.dataset_id == dataset_id,
            CoverageSnapshot.ruleset_id_text == ruleset_id,
        )
        .order_by(CoverageSnapshot.created_at.desc())
        .first()
    )
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="coverage snapshot not found")

    top_gaps = _top_gaps_for_dataset(db=db, dataset_id=dataset_id)
    merged_count = _rules_merged_count(db=db)
    validated_count = (
        db.query(func.count(ReplayValidation.id))
        .filter(
            ReplayValidation.attack_dataset_id == dataset_id,
            ReplayValidation.verdict == "PASS",
        )
        .scalar()
        or 0
    )

    response = AuditCoverageSnapshotResponse(
        dataset_id=dataset_id,
        ruleset_id=ruleset_id,
        snapshot_id=str(snapshot.id),
        metrics_json=snapshot.metrics_json or snapshot.summary or {},
        top_gaps=top_gaps,
        rules_merged_count=int(merged_count),
        rules_validated_count=int(validated_count),
        generated_at=_utc_now(),
    )
    if format.lower() == "markdown":
        return PlainTextResponse(_coverage_snapshot_markdown(response))
    return response


@router.get("/coverage/diff")
def export_coverage_diff(
    dataset_id: str = Query(...),
    from_ruleset: str = Query(...),
    to_ruleset: str = Query(...),
    format: str = Query("json"),
    db: Session = Depends(get_db),
) -> Any:
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="coverage snapshots for diff not found")

    from_rate = _coverage_rate(from_snapshot.metrics_json, from_snapshot.coverage_percent)
    to_rate = _coverage_rate(to_snapshot.metrics_json, to_snapshot.coverage_percent)
    delta = None if from_rate is None or to_rate is None else round(to_rate - from_rate, 4)

    from_not_covered = _metric_int(from_snapshot.metrics_json, "not_covered_count")
    to_not_covered = _metric_int(to_snapshot.metrics_json, "not_covered_count")
    gaps_closed = None if from_not_covered is None or to_not_covered is None else (from_not_covered - to_not_covered)

    rules_responsible = _rules_merged_between(
        db=db,
        start=from_snapshot.computed_at or from_snapshot.created_at,
        end=to_snapshot.computed_at or to_snapshot.created_at,
    )
    replay_refs = _replay_validation_refs(
        db=db,
        dataset_id=dataset_id,
        start=from_snapshot.computed_at or from_snapshot.created_at,
        end=to_snapshot.computed_at or to_snapshot.created_at,
    )

    response = AuditCoverageDiffResponse(
        dataset_id=dataset_id,
        from_ruleset=from_ruleset,
        to_ruleset=to_ruleset,
        coverage_rate_delta=delta,
        gaps_closed_count=gaps_closed,
        rules_responsible=rules_responsible,
        replay_validation_refs=replay_refs,
        generated_at=_utc_now(),
    )
    if format.lower() == "markdown":
        return PlainTextResponse(_coverage_diff_markdown(response))
    return response


@router.get("/runs/{run_id}/report")
def export_run_report(
    run_id: UUID,
    format: str = Query("json"),
    db: Session = Depends(get_db),
) -> Any:
    run = db.query(AttackRun).filter(AttackRun.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="run not found")

    findings = (
        db.query(Finding)
        .filter(or_(Finding.run_id == run_id, Finding.attack_run_id == run_id))
        .order_by(Finding.created_at.asc())
        .all()
    )
    evaluations = (
        db.query(CoverageEvaluation)
        .filter(or_(CoverageEvaluation.run_id == run_id, CoverageEvaluation.attack_run_id == run_id))
        .order_by(CoverageEvaluation.evaluated_at.asc())
        .all()
    )
    evaluation_ids = [item.id for item in evaluations]
    proposals = (
        db.query(RuleProposal)
        .filter(RuleProposal.evaluation_id.in_(evaluation_ids))
        .order_by(RuleProposal.created_at.asc())
        .all()
        if evaluation_ids
        else []
    )
    proposal_ids = [item.id for item in proposals]
    validations = (
        db.query(ReplayValidation)
        .filter(or_(ReplayValidation.attack_run_id == run_id, ReplayValidation.proposal_id.in_(proposal_ids)))
        .order_by(ReplayValidation.created_at.asc())
        .all()
        if proposal_ids
        else db.query(ReplayValidation).filter(ReplayValidation.attack_run_id == run_id).all()
    )

    response = AuditRunReportResponse(
        run_id=str(run.id),
        run_metadata={
            "run_id": str(run.id),
            "name": run.name,
            "dataset_id": run.dataset_id,
            "attack_source": run.attack_source,
            "status": run.status,
            "start_time": _datetime_to_utc_iso(run.start_time),
            "end_time": _datetime_to_utc_iso(run.end_time),
        },
        findings=[
            {
                "finding_id": str(item.id),
                "finding_type": item.finding_type,
                "severity": item.severity,
                "title": item.title,
                "occurred_at": _datetime_to_utc_iso(item.occurred_at),
            }
            for item in findings
        ],
        coverage_evaluations=[
            {
                "evaluation_id": str(item.id),
                "finding_id": str(item.finding_id) if item.finding_id else None,
                "coverage_state": item.coverage_state,
                "result": item.result,
                "evaluated_at": _datetime_to_utc_iso(item.evaluated_at),
            }
            for item in evaluations
        ],
        rule_proposals=[
            {
                "proposal_id": str(item.id),
                "rule_id": item.rule_id,
                "rule_version": item.rule_version,
                "proposal_status": item.proposal_status or item.status,
            }
            for item in proposals
        ],
        replay_validations=[
            {
                "validation_id": str(item.id),
                "proposal_id": str(item.proposal_id) if item.proposal_id else None,
                "verdict": item.verdict,
                "attack_dataset_id": item.attack_dataset_id,
            }
            for item in validations
        ],
        generated_at=_utc_now(),
    )
    if format.lower() == "markdown":
        return PlainTextResponse(_run_report_markdown(response))
    return response


def _top_gaps_for_dataset(db: Session, dataset_id: str) -> list[dict[str, Any]]:
    run_ids = [item[0] for item in db.query(AttackRun.id).filter(AttackRun.dataset_id == dataset_id).all()]
    if not run_ids:
        return []

    rows = (
        db.query(
            Finding.finding_type,
            Finding.severity,
            func.count(Finding.id).label("count"),
        )
        .join(CoverageEvaluation, CoverageEvaluation.finding_id == Finding.id)
        .filter(
            CoverageEvaluation.run_id.in_(run_ids),
            CoverageEvaluation.coverage_state.in_(["not_covered", "partially_covered"]),
        )
        .group_by(Finding.finding_type, Finding.severity)
        .order_by(func.count(Finding.id).desc())
        .limit(10)
        .all()
    )
    return [
        {
            "finding_type": row[0],
            "severity": row[1],
            "count": int(row[2]),
        }
        for row in rows
    ]


def _rules_merged_count(db: Session) -> int:
    merged = (
        db.query(func.count(RuleProposal.id))
        .filter(
            or_(
                RuleProposal.proposal_status.in_(["merged", "approved"]),
                RuleProposal.status.in_(["merged", "approved"]),
            )
        )
        .scalar()
    )
    return int(merged or 0)


def _rules_merged_between(db: Session, start: datetime, end: datetime) -> list[str]:
    rows = (
        db.query(RuleProposal.rule_id)
        .filter(
            RuleProposal.rule_id.isnot(None),
            RuleProposal.created_at >= start,
            RuleProposal.created_at <= end,
            or_(
                RuleProposal.proposal_status.in_(["merged", "approved"]),
                RuleProposal.status.in_(["merged", "approved"]),
            ),
        )
        .all()
    )
    deduped: list[str] = []
    for row in rows:
        rule_id = row[0]
        if isinstance(rule_id, str) and rule_id not in deduped:
            deduped.append(rule_id)
    return deduped


def _replay_validation_refs(db: Session, dataset_id: str, start: datetime, end: datetime) -> list[str]:
    rows = (
        db.query(ReplayValidation.id)
        .filter(
            ReplayValidation.attack_dataset_id == dataset_id,
            ReplayValidation.verdict == "PASS",
            ReplayValidation.created_at >= start,
            ReplayValidation.created_at <= end,
        )
        .all()
    )
    return [str(row[0]) for row in rows]


def _coverage_rate(metrics_json: Optional[dict[str, Any]], fallback: Optional[float]) -> Optional[float]:
    if isinstance(metrics_json, dict):
        value = metrics_json.get("coverage_rate")
        if isinstance(value, (int, float)):
            return round(float(value), 4)
    if fallback is None:
        return None
    return round(float(fallback), 4)


def _metric_int(metrics_json: Optional[dict[str, Any]], key: str) -> Optional[int]:
    if not isinstance(metrics_json, dict):
        return None
    value = metrics_json.get(key)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


def _coverage_snapshot_markdown(payload: AuditCoverageSnapshotResponse) -> str:
    lines = [
        f"# Coverage Snapshot: {payload.dataset_id} / {payload.ruleset_id}",
        "",
        "## Metrics",
    ]
    for key, value in payload.metrics_json.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Top Gaps"])
    if payload.top_gaps:
        for item in payload.top_gaps:
            lines.append(
                f"- {item.get('finding_type')} ({item.get('severity')}): {item.get('count')}"
            )
    else:
        lines.append("- No uncovered gaps recorded.")
    lines.extend(
        [
            "",
            f"- Rules merged: {payload.rules_merged_count}",
            f"- Rules validated: {payload.rules_validated_count}",
        ]
    )
    return "\n".join(lines)


def _coverage_diff_markdown(payload: AuditCoverageDiffResponse) -> str:
    lines = [
        f"# Coverage Diff: {payload.dataset_id}",
        f"- From: {payload.from_ruleset}",
        f"- To: {payload.to_ruleset}",
        f"- coverage_rate_delta: {payload.coverage_rate_delta}",
        f"- gaps_closed_count: {payload.gaps_closed_count}",
        "",
        "## Rules Responsible",
    ]
    if payload.rules_responsible:
        lines.extend([f"- {item}" for item in payload.rules_responsible])
    else:
        lines.append("- None")
    lines.extend(["", "## Replay Validation References"])
    if payload.replay_validation_refs:
        lines.extend([f"- {item}" for item in payload.replay_validation_refs])
    else:
        lines.append("- None")
    return "\n".join(lines)


def _run_report_markdown(payload: AuditRunReportResponse) -> str:
    lines = [
        f"# Run Report: {payload.run_id}",
        "",
        "## Run Metadata",
    ]
    for key, value in payload.run_metadata.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            f"- Findings: {len(payload.findings)}",
            f"- Coverage evaluations: {len(payload.coverage_evaluations)}",
            f"- Rule proposals: {len(payload.rule_proposals)}",
            f"- Replay validations: {len(payload.replay_validations)}",
        ]
    )
    return "\n".join(lines)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _datetime_to_utc_iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
