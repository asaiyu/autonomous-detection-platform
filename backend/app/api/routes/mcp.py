from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Text, cast
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.detection.replay_service import replay_dataset
from app.models.alert import Alert
from app.models.case import CaseRecord
from app.models.event import Event
from app.models.rule_proposal import RuleProposal
from app.schemas.mcp import (
    CreateRuleProposalToolRequest,
    GetAlertContextToolRequest,
    RunReplayToolRequest,
    SearchAlertsToolRequest,
    SearchEventsToolRequest,
)

router = APIRouter()


@router.post("/search_events")
def mcp_search_events(payload: SearchEventsToolRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    query = db.query(Event)
    if payload.start is not None:
        query = query.filter(Event.occurred_at >= _ensure_utc(payload.start))
    if payload.end is not None:
        query = query.filter(Event.occurred_at <= _ensure_utc(payload.end))
    if payload.query:
        query = query.filter(cast(Event.canonical_event_json, Text).ilike(f"%{payload.query}%"))

    rows = query.order_by(Event.occurred_at.desc()).limit(payload.limit).all()
    return {
        "tool": "search_events",
        "count": len(rows),
        "items": [
            {
                "event_id": str(row.id),
                "timestamp": _to_utc_iso(row.occurred_at),
                "source_type": row.source,
                "event_type": row.event_type,
            }
            for row in rows
        ],
    }


@router.post("/search_alerts")
def mcp_search_alerts(payload: SearchAlertsToolRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    query = db.query(Alert)
    if payload.start is not None:
        query = query.filter(Alert.created_at >= _ensure_utc(payload.start))
    if payload.end is not None:
        query = query.filter(Alert.created_at <= _ensure_utc(payload.end))
    if payload.query:
        query = query.filter(cast(Alert.evidence_json, Text).ilike(f"%{payload.query}%") | Alert.title.ilike(f"%{payload.query}%"))

    rows = query.order_by(Alert.created_at.desc()).limit(payload.limit).all()
    return {
        "tool": "search_alerts",
        "count": len(rows),
        "items": [
            {
                "alert_id": str(row.id),
                "title": row.title,
                "severity": row.severity,
                "status": row.status,
                "created_at": _to_utc_iso(row.created_at),
            }
            for row in rows
        ],
    }


@router.post("/get_alert_context")
def mcp_get_alert_context(payload: GetAlertContextToolRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    alert = db.query(Alert).filter(Alert.id == payload.alert_id).first()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="alert not found")

    case = db.query(CaseRecord).filter(CaseRecord.alert_id == payload.alert_id).first()

    evidence_events: list[dict[str, Any]] = []
    for raw_event_id in alert.evidence_event_ids or []:
        try:
            event_uuid = UUID(str(raw_event_id))
        except ValueError:
            continue
        event = db.query(Event).filter(Event.id == event_uuid).first()
        if event is None:
            continue
        evidence_events.append(
            {
                "event_id": str(event.id),
                "timestamp": _to_utc_iso(event.occurred_at),
                "source_type": event.source,
                "canonical_event_json": event.canonical_event_json,
            }
        )

    return {
        "tool": "get_alert_context",
        "alert": {
            "alert_id": str(alert.id),
            "rule_id": alert.rule_id,
            "severity": alert.severity,
            "status": alert.status,
            "evidence_event_ids": alert.evidence_event_ids or [],
            "evidence_json": alert.evidence_json or {},
        },
        "case": (
            {
                "case_id": str(case.id),
                "notes_markdown": case.notes_markdown,
                "triage_json": case.triage_json,
            }
            if case is not None
            else None
        ),
        "events": evidence_events,
    }


@router.post("/run_replay")
def mcp_run_replay(payload: RunReplayToolRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        result = replay_dataset(
            dataset_id=payload.dataset_id,
            ruleset_id=payload.ruleset_id,
            mode=payload.mode,
            db=db,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "tool": "run_replay",
        "result": {
            "dataset_id": result.dataset_id,
            "ruleset_id": result.ruleset_id,
            "mode": result.mode,
            "alerts_generated": result.alerts_generated,
            "attack_tp_count": result.attack_tp_count,
            "baseline_fp_count": result.baseline_fp_count,
            "coverage_rate": result.coverage_rate,
            "verdict": result.verdict,
            "sample_alert_ids": result.sample_alert_ids,
            "sample_event_ids": result.sample_event_ids,
        },
    }


@router.post("/create_rule_proposal")
def mcp_create_rule_proposal(payload: CreateRuleProposalToolRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    proposal = RuleProposal(
        title=payload.title,
        rule_id=payload.rule_id,
        rule_version=payload.rule_version,
        rule_yaml=payload.rule_yaml,
        rationale=payload.rationale,
        status="pending",
        proposal_status="pending",
        created_by=payload.created_by,
        references_json=payload.references_json,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return {
        "tool": "create_rule_proposal",
        "proposal_id": str(proposal.id),
        "status": proposal.status,
    }


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _to_utc_iso(value: datetime) -> str:
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")
