from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.detection.field_access import get_field
from app.detection.operators import evaluate_operator
from app.detection.types import AlertMatch, RuleDefinition


class DetectionEngine:
    def __init__(self, rules: list[RuleDefinition]) -> None:
        self.rules = sorted(rules, key=lambda rule: rule.id)

    def evaluate_events(self, events: list[dict[str, Any]]) -> list[AlertMatch]:
        ordered_events = sorted(events, key=_event_sort_key)
        matches: list[AlertMatch] = []

        for rule in self.rules:
            if rule.detect_type == "single":
                matches.extend(self._evaluate_single(rule, ordered_events))
            elif rule.detect_type == "sequence":
                matches.extend(self._evaluate_sequence(rule, ordered_events))

        return sorted(matches, key=lambda item: (item.matched_at, item.rule_id, item.evidence_event_ids))

    def _evaluate_single(self, rule: RuleDefinition, events: list[dict[str, Any]]) -> list[AlertMatch]:
        where = rule.detect.get("where", {})
        matches: list[AlertMatch] = []

        for event in events:
            if not _matches_log_source(rule, event):
                continue
            if evaluate_condition(where, event):
                matches.append(_build_single_match(rule, event))

        return matches

    def _evaluate_sequence(self, rule: RuleDefinition, events: list[dict[str, Any]]) -> list[AlertMatch]:
        stages = rule.detect.get("stages", [])
        if len(stages) != 2:
            return []

        stage1_where = stages[0].get("where", {})
        stage2_where = stages[1].get("where", {})
        join_keys = [str(key) for key in rule.detect.get("join_keys", [])]
        window_seconds = int(rule.detect.get("window_seconds", 0))

        stage1_buffer: list[dict[str, Any]] = []
        matches: list[AlertMatch] = []

        for event in events:
            current_ts = _event_timestamp(event)
            stage1_buffer = [
                buffered
                for buffered in stage1_buffer
                if (current_ts - _event_timestamp(buffered)).total_seconds() <= window_seconds
            ]

            if _matches_log_source(rule, event) and evaluate_condition(stage2_where, event):
                for previous in stage1_buffer:
                    if _sequence_matches(previous, event, join_keys, window_seconds):
                        matches.append(_build_sequence_match(rule, previous, event))
                        break

            if _matches_log_source(rule, event) and evaluate_condition(stage1_where, event):
                stage1_buffer.append(event)

        return matches


def evaluate_condition(condition: Any, event: dict[str, Any]) -> bool:
    if not isinstance(condition, dict):
        return False

    if "all" in condition:
        clauses = condition.get("all", [])
        if not isinstance(clauses, list):
            return False
        return all(evaluate_condition(clause, event) for clause in clauses)

    if "any" in condition:
        clauses = condition.get("any", [])
        if not isinstance(clauses, list):
            return False
        return any(evaluate_condition(clause, event) for clause in clauses)

    if "not" in condition:
        return not evaluate_condition(condition.get("not"), event)

    field = condition.get("field")
    op = condition.get("op")
    if not isinstance(field, str) or not isinstance(op, str):
        return False

    left = get_field(event, field)
    right = condition.get("value")
    return evaluate_operator(op=op, left=left, right=right)


def _build_single_match(rule: RuleDefinition, event: dict[str, Any]) -> AlertMatch:
    event_id = _event_id(event)
    return AlertMatch(
        rule_id=rule.id,
        rule_version=rule.version,
        severity=rule.severity,
        title=str(rule.output.get("alert_title", rule.name)),
        category=str(rule.output.get("alert_category", "uncategorized")),
        alert_type=str(rule.output.get("alert_type", "generic")),
        confidence=float(rule.output.get("confidence", 0.5)),
        status=str(rule.output.get("default_status", "open")),
        description=rule.description,
        evidence_event_ids=[event_id] if event_id else [],
        evidence_json=_extract_evidence_single(event, rule.evidence_fields),
        matched_at=_event_timestamp(event),
        source_event_id=event_id,
    )


def _build_sequence_match(rule: RuleDefinition, stage1_event: dict[str, Any], stage2_event: dict[str, Any]) -> AlertMatch:
    stage1_id = _event_id(stage1_event)
    stage2_id = _event_id(stage2_event)
    event_ids = [event_id for event_id in (stage1_id, stage2_id) if event_id]

    return AlertMatch(
        rule_id=rule.id,
        rule_version=rule.version,
        severity=rule.severity,
        title=str(rule.output.get("alert_title", rule.name)),
        category=str(rule.output.get("alert_category", "uncategorized")),
        alert_type=str(rule.output.get("alert_type", "generic")),
        confidence=float(rule.output.get("confidence", 0.5)),
        status=str(rule.output.get("default_status", "open")),
        description=rule.description,
        evidence_event_ids=event_ids,
        evidence_json=_extract_evidence_sequence(stage1_event, stage2_event, rule.evidence_fields),
        matched_at=_event_timestamp(stage2_event),
        source_event_id=stage2_id,
    )


def _extract_evidence_single(event: dict[str, Any], include_fields: list[str]) -> dict[str, Any]:
    if not include_fields:
        return {"event": event}
    return {field: get_field(event, field) for field in include_fields}


def _extract_evidence_sequence(
    stage1_event: dict[str, Any],
    stage2_event: dict[str, Any],
    include_fields: list[str],
) -> dict[str, Any]:
    if not include_fields:
        return {"stage1": stage1_event, "stage2": stage2_event}

    return {
        "stage1": {field: get_field(stage1_event, field) for field in include_fields},
        "stage2": {field: get_field(stage2_event, field) for field in include_fields},
    }


def _matches_log_source(rule: RuleDefinition, event: dict[str, Any]) -> bool:
    if not rule.log_sources:
        return True
    source_type = get_field(event, "source.type")
    return isinstance(source_type, str) and source_type in rule.log_sources


def _sequence_matches(
    stage1_event: dict[str, Any],
    stage2_event: dict[str, Any],
    join_keys: list[str],
    window_seconds: int,
) -> bool:
    ts1 = _event_timestamp(stage1_event)
    ts2 = _event_timestamp(stage2_event)

    if ts2 < ts1:
        return False
    if (ts2 - ts1).total_seconds() > window_seconds:
        return False

    for key in join_keys:
        left = get_field(stage1_event, key)
        right = get_field(stage2_event, key)
        if left is None or right is None or left != right:
            return False

    return True


def _event_id(event: dict[str, Any]) -> str | None:
    event_id = get_field(event, "event_id")
    if isinstance(event_id, str):
        return event_id
    return None


def _event_sort_key(event: dict[str, Any]) -> tuple[datetime, str]:
    return _event_timestamp(event), _event_id(event) or ""


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
