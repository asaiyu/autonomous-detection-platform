from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.detection.engine import DetectionEngine
from app.detection.field_access import get_field
from app.detection.rule_loader import load_rules
from app.detection.types import AlertMatch, ReplayResult
from app.models.alert import Alert
from app.models.event import Event

_ALLOWED_FP_THRESHOLD = 2


def replay_dataset(dataset_id: str, ruleset_id: str, mode: str, db: Session) -> ReplayResult:
    started_at = _utc_now()

    if mode not in {"attack_validation", "baseline_validation", "full_evaluation"}:
        raise ValueError(f"unsupported replay mode: {mode}")

    dataset_dir = resolve_datasets_dir() / dataset_id
    if not dataset_dir.exists():
        raise FileNotFoundError(f"dataset not found: {dataset_dir}")

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
    )

    attack_tp_count = len(attack_matches)
    baseline_fp_count = len(baseline_matches)
    coverage_rate = _compute_coverage_rate(dataset_dir=dataset_dir, attack_matches=attack_matches)

    verdict = "PASS" if attack_tp_count >= 1 and baseline_fp_count <= _ALLOWED_FP_THRESHOLD else "FAIL"

    finished_at = _utc_now()

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
            },
        )
        db.add(alert)
        created.append(alert)

    db.commit()
    for alert in created:
        db.refresh(alert)

    return [str(alert.id) for alert in created]


def _resolve_source_event_uuid(db: Session, raw_event_id: str | None) -> uuid.UUID | None:
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


def _compute_coverage_rate(dataset_dir: Path, attack_matches: list[AlertMatch]) -> float | None:
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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
