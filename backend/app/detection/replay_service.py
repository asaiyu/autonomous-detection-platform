from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.detection.engine import DetectionEngine
from app.detection.field_access import get_field
from app.detection.rule_loader import load_rules
from app.detection.types import AlertMatch, ReplayResult
from app.models.alert import Alert
from app.models.attack_run import AttackRun
from app.models.coverage_evaluation import CoverageEvaluation
from app.models.coverage_snapshot import CoverageSnapshot
from app.models.event import Event
from app.models.finding import Finding
from app.models.replay_validation import ReplayValidation
from app.models.ruleset import Ruleset

_ALLOWED_FP_THRESHOLD = 2


def replay_dataset(dataset_id: str, ruleset_id: str, mode: str, db: Session) -> ReplayResult:
    started_dt = datetime.now(timezone.utc)
    started_at = _to_utc_iso(started_dt)

    if mode not in {"attack_validation", "baseline_validation", "full_evaluation"}:
        raise ValueError(f"unsupported replay mode: {mode}")

    dataset_dir = resolve_datasets_dir() / dataset_id
    if not dataset_dir.exists():
        raise FileNotFoundError(f"dataset not found: {dataset_dir}")

    ruleset = _get_or_create_ruleset(db=db, ruleset_id=ruleset_id)
    replay_run = _create_replay_run(db=db, dataset_id=dataset_id, mode=mode, started_dt=started_dt)

    rules = load_rules(ruleset_id=ruleset_id)
    engine = DetectionEngine(rules)

    attack_events = _load_events_file(dataset_dir / "events.ndjson")
    baseline_events = _load_events_file(dataset_dir / "baseline.ndjson", required=False)

    attack_matches: list[AlertMatch] = []
    baseline_matches: list[AlertMatch] = []

    if mode in {"attack_validation", "full_evaluation"}:
        attack_matches = engine.evaluate_events(attack_events)
    if mode in {"baseline_validation", "full_evaluation"}:
        baseline_matches = engine.evaluate_events(baseline_events)

    created_alert_ids = _persist_alerts(
        db=db,
        matches=[*attack_matches, *baseline_matches],
        dataset_id=dataset_id,
        ruleset_id=ruleset_id,
        mode=mode,
        replay_run_id=replay_run.id,
    )

    attack_tp_count = len(attack_matches)
    baseline_fp_count = len(baseline_matches)
    coverage_rate = _compute_coverage_rate(dataset_dir=dataset_dir, attack_matches=attack_matches)

    verdict = "PASS" if attack_tp_count >= 1 and baseline_fp_count <= _ALLOWED_FP_THRESHOLD else "FAIL"

    finished_dt = datetime.now(timezone.utc)
    finished_at = _to_utc_iso(finished_dt)
    replay_run.status = "completed"
    replay_run.end_time = finished_dt
    replay_run.finished_at = finished_dt
    replay_run.summary = f"Replay {verdict}: tp={attack_tp_count} fp={baseline_fp_count}"

    _persist_findings_and_coverage_evaluations(
        db=db,
        dataset_dir=dataset_dir,
        replay_run_id=replay_run.id,
        finished_dt=finished_dt,
        attack_matches=attack_matches,
    )

    _persist_replay_artifacts(
        db=db,
        dataset_id=dataset_id,
        ruleset_id=ruleset_id,
        ruleset_uuid=ruleset.id,
        replay_run_id=replay_run.id,
        mode=mode,
        attack_tp_count=attack_tp_count,
        baseline_fp_count=baseline_fp_count,
        coverage_rate=coverage_rate,
        alerts_generated=len(created_alert_ids),
        verdict=verdict,
        allowed_fp_threshold=_ALLOWED_FP_THRESHOLD,
        started_dt=started_dt,
        finished_dt=finished_dt,
    )

    return ReplayResult(
        dataset_id=dataset_id,
        ruleset_id=ruleset_id,
        mode=mode,
        alerts_generated=len(created_alert_ids),
        attack_tp_count=attack_tp_count,
        baseline_fp_count=baseline_fp_count,
        coverage_rate=coverage_rate,
        verdict=verdict,
        allowed_fp_threshold=_ALLOWED_FP_THRESHOLD,
        sample_alert_ids=created_alert_ids[:10],
        sample_event_ids=_sample_event_ids([*attack_matches, *baseline_matches]),
        started_at=started_at,
        finished_at=finished_at,
    )


def resolve_datasets_dir() -> Path:
    env_value = os.getenv("DATASETS_DIR")
    if env_value:
        return Path(env_value)

    project_root = Path(__file__).resolve().parents[3]
    candidates = [Path("/datasets"), project_root / "datasets"]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[-1]


def _persist_alerts(
    db: Session,
    matches: list[AlertMatch],
    dataset_id: str,
    ruleset_id: str,
    mode: str,
    replay_run_id: uuid.UUID,
) -> list[str]:
    created: list[Alert] = []

    for match in matches:
        source_event_uuid = _resolve_source_event_uuid(db, match.source_event_id)

        alert = Alert(
            event_id=source_event_uuid,
            rule_id=match.rule_id,
            rule_version=match.rule_version,
            severity=match.severity,
            title=match.title,
            category=match.category,
            alert_type=match.alert_type,
            status=match.status,
            confidence=match.confidence,
            description=match.description,
            evidence_event_ids=match.evidence_event_ids,
            evidence_json=match.evidence_json,
            extra={
                "dataset_id": dataset_id,
                "ruleset_id": ruleset_id,
                "replay_mode": mode,
                "run_id": str(replay_run_id),
            },
        )
        db.add(alert)
        created.append(alert)

    db.commit()
    for alert in created:
        db.refresh(alert)

    return [str(alert.id) for alert in created]


def _resolve_source_event_uuid(db: Session, raw_event_id: Optional[str]) -> Optional[uuid.UUID]:
    if raw_event_id is None:
        return None

    try:
        candidate = uuid.UUID(raw_event_id)
    except ValueError:
        return None

    exists = db.query(Event.id).filter(Event.id == candidate).first()
    if exists is None:
        return None
    return candidate


def _compute_coverage_rate(dataset_dir: Path, attack_matches: list[AlertMatch]) -> Optional[float]:
    findings_path = dataset_dir / "findings.json"
    if not findings_path.exists():
        return None

    payload = json.loads(findings_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        return None

    alerted_event_ids = set(_sample_event_ids(attack_matches, limit=100000))
    covered = 0
    total = 0

    for finding in payload:
        if not isinstance(finding, dict):
            continue
        total += 1
        finding_event_ids = _extract_finding_event_ids(finding)
        if any(event_id in alerted_event_ids for event_id in finding_event_ids):
            covered += 1

    if total == 0:
        return None
    return round(covered / total, 4)


def _extract_finding_event_ids(finding: dict[str, Any]) -> list[str]:
    event_ids: list[str] = []

    direct = finding.get("event_id")
    if isinstance(direct, str):
        event_ids.append(direct)

    evidence_event_ids = finding.get("evidence_event_ids")
    if isinstance(evidence_event_ids, list):
        event_ids.extend([item for item in evidence_event_ids if isinstance(item, str)])

    entrypoint = finding.get("entrypoint_json")
    if isinstance(entrypoint, dict):
        event_id = entrypoint.get("event_id")
        if isinstance(event_id, str):
            event_ids.append(event_id)

    return event_ids


def _sample_event_ids(matches: list[AlertMatch], limit: int = 10) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    for match in matches:
        for event_id in match.evidence_event_ids:
            if event_id not in seen:
                seen.add(event_id)
                ordered.append(event_id)
                if len(ordered) >= limit:
                    return ordered

    return ordered


def _load_events_file(path: Path, required: bool = True) -> list[dict[str, Any]]:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"events file not found: {path}")
        return []

    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"invalid event record at {path}:{line_number}")
        events.append(payload)

    return sorted(events, key=lambda event: (_event_timestamp(event), str(get_field(event, "event_id") or "")))


def _persist_replay_artifacts(
    db: Session,
    dataset_id: str,
    ruleset_id: str,
    ruleset_uuid: uuid.UUID,
    replay_run_id: uuid.UUID,
    mode: str,
    attack_tp_count: int,
    baseline_fp_count: int,
    coverage_rate: Optional[float],
    alerts_generated: int,
    verdict: str,
    allowed_fp_threshold: int,
    started_dt: datetime,
    finished_dt: datetime,
) -> None:
    results_json: dict[str, Any] = {
        "dataset_id": dataset_id,
        "ruleset_id": ruleset_id,
        "mode": mode,
        "alerts_generated": alerts_generated,
        "attack_tp_count": attack_tp_count,
        "baseline_fp_count": baseline_fp_count,
        "coverage_rate": coverage_rate,
        "allowed_fp_threshold": allowed_fp_threshold,
    }

    validation = ReplayValidation(
        attack_run_id=replay_run_id,
        attack_dataset_id=dataset_id if mode in {"attack_validation", "full_evaluation"} else None,
        baseline_dataset_id=dataset_id if mode in {"baseline_validation", "full_evaluation"} else None,
        replay_started_at=started_dt,
        replay_finished_at=finished_dt,
        results_json=results_json,
        verdict=verdict,
        report=f"Replay {verdict}: tp={attack_tp_count} fp={baseline_fp_count}",
        status=verdict.lower(),
        details=results_json,
        validated_at=finished_dt,
    )
    db.add(validation)

    metrics_json: dict[str, Any] = {
        "coverage_rate": coverage_rate,
        "attack_tp_count": attack_tp_count,
        "baseline_fp_count": baseline_fp_count,
        "alerts_generated": alerts_generated,
    }
    snapshot = CoverageSnapshot(
        ruleset_id=ruleset_uuid,
        dataset_id=dataset_id,
        ruleset_id_text=ruleset_id,
        computed_at=finished_dt,
        metrics_json=metrics_json,
        coverage_percent=coverage_rate if coverage_rate is not None else 0.0,
        summary=metrics_json,
    )
    db.add(snapshot)
    db.commit()


def _event_timestamp(event: dict[str, Any]) -> datetime:
    raw = get_field(event, "timestamp")
    if isinstance(raw, str) and raw:
        value = raw
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def _to_utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_or_create_ruleset(db: Session, ruleset_id: str) -> Ruleset:
    existing = db.query(Ruleset).filter(Ruleset.ruleset_id == ruleset_id).first()
    if existing is not None:
        return existing

    ruleset = Ruleset(
        ruleset_id=ruleset_id,
        name=ruleset_id,
        version=ruleset_id,
        note="auto-created by replay",
        is_active=False,
        rules={},
    )
    db.add(ruleset)
    db.flush()
    return ruleset


def _create_replay_run(db: Session, dataset_id: str, mode: str, started_dt: datetime) -> AttackRun:
    run = AttackRun(
        name=f"replay:{dataset_id}:{mode}",
        attack_source="replay",
        dataset_id=dataset_id,
        status="running",
        start_time=started_dt,
        started_at=started_dt,
    )
    db.add(run)
    db.flush()
    return run


def _persist_findings_and_coverage_evaluations(
    db: Session,
    dataset_dir: Path,
    replay_run_id: uuid.UUID,
    finished_dt: datetime,
    attack_matches: list[AlertMatch],
) -> None:
    findings_path = dataset_dir / "findings.json"
    if not findings_path.exists():
        return

    payload = json.loads(findings_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        return

    alerted_event_ids = set(_sample_event_ids(attack_matches, limit=100000))
    for finding_item in payload:
        if not isinstance(finding_item, dict):
            continue

        finding_event_ids = _extract_finding_event_ids(finding_item)
        covered = any(event_id in alerted_event_ids for event_id in finding_event_ids)
        coverage_state = "covered" if covered else "not_covered"

        finding = Finding(
            attack_run_id=replay_run_id,
            run_id=replay_run_id,
            finding_type=str(finding_item.get("finding_type") or finding_item.get("type") or "unknown"),
            title=_as_optional_str(finding_item.get("title")),
            severity=_as_optional_str(finding_item.get("severity")),
            technique=_as_optional_str(finding_item.get("technique")),
            entrypoint_json=_as_optional_dict(finding_item.get("entrypoint_json")),
            proof_json=_as_optional_dict(finding_item.get("proof_json")),
            tags_json=_as_optional_dict(finding_item.get("tags_json")),
            occurred_at=_parse_optional_timestamp(finding_item.get("occurred_at")),
        )
        db.add(finding)
        db.flush()

        evaluation = CoverageEvaluation(
            attack_run_id=replay_run_id,
            run_id=replay_run_id,
            finding_id=finding.id,
            scenario=f"replay:{dataset_dir.name}",
            result="detected" if covered else "missed",
            coverage_state=coverage_state,
            window_end=finished_dt,
            related_event_ids_json={"event_ids": finding_event_ids},
            notes="auto-generated by replay",
            evaluated_at=finished_dt,
        )
        db.add(evaluation)

    db.commit()


def _as_optional_dict(value: Any) -> Optional[dict[str, Any]]:
    if isinstance(value, dict):
        return value
    return None


def _as_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _parse_optional_timestamp(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None

    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
