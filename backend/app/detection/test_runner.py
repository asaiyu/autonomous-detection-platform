from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.detection.engine import DetectionEngine
from app.detection.replay_service import _load_events_file
from app.detection.rule_loader import load_rules


@dataclass(frozen=True)
class RuleTestFailure:
    rule_id: str
    message: str


@dataclass(frozen=True)
class RuleTestSummary:
    total: int
    passed: int
    failed: int
    failures: list[RuleTestFailure]


def run_rule_tests(rules_dir: Path | None = None, tests_dir: Path | None = None) -> RuleTestSummary:
    rules = {rule.id: rule for rule in load_rules(rules_dir=rules_dir)}

    fixtures_dir = tests_dir or resolve_rule_tests_dir()
    if not fixtures_dir.exists():
        raise FileNotFoundError(f"rule test fixtures directory not found: {fixtures_dir}")

    failures: list[RuleTestFailure] = []
    total = 0

    for rule_dir in sorted([path for path in fixtures_dir.iterdir() if path.is_dir()]):
        total += 1
        rule_id = rule_dir.name

        rule = rules.get(rule_id)
        if rule is None:
            failures.append(RuleTestFailure(rule_id=rule_id, message="rule yaml not found"))
            continue

        events_path = rule_dir / "events.ndjson"
        expected_path = rule_dir / "expected_alerts.json"
        if not events_path.exists() or not expected_path.exists():
            failures.append(RuleTestFailure(rule_id=rule_id, message="missing events.ndjson or expected_alerts.json"))
            continue

        events = _load_events_file(events_path)
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        if not isinstance(expected, dict):
            failures.append(RuleTestFailure(rule_id=rule_id, message="expected_alerts.json must be an object"))
            continue

        matches = DetectionEngine([rule]).evaluate_events(events)

        should_fire_actual = len(matches) > 0
        should_fire_expected = bool(expected.get("should_fire", False))
        expected_count = int(expected.get("expected_count", 0))
        actual_count = len(matches)

        if should_fire_actual != should_fire_expected:
            failures.append(
                RuleTestFailure(
                    rule_id=rule_id,
                    message=f"should_fire mismatch: expected {should_fire_expected}, got {should_fire_actual}",
                )
            )

        if actual_count != expected_count:
            failures.append(
                RuleTestFailure(
                    rule_id=rule_id,
                    message=f"expected_count mismatch: expected {expected_count}, got {actual_count}",
                )
            )

        expected_ids = expected.get("evidence_event_ids_contains", [])
        if isinstance(expected_ids, list):
            actual_ids = {event_id for match in matches for event_id in match.evidence_event_ids}
            missing_ids = [item for item in expected_ids if isinstance(item, str) and item not in actual_ids]
            if missing_ids:
                failures.append(
                    RuleTestFailure(
                        rule_id=rule_id,
                        message=f"missing expected evidence_event_ids: {missing_ids}",
                    )
                )

    failing_rules = {failure.rule_id for failure in failures}
    failed = len(failing_rules)
    passed = max(total - failed, 0)
    return RuleTestSummary(total=total, passed=passed, failed=failed, failures=failures)


def resolve_rule_tests_dir() -> Path:
    env_value = os.getenv("RULE_TESTS_DIR")
    if env_value:
        return Path(env_value)

    project_root = Path(__file__).resolve().parents[3]
    candidates = [Path("/tests/rules"), project_root / "tests" / "rules"]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[-1]


def _print_summary(summary: RuleTestSummary) -> None:
    print(f"Rule tests: total={summary.total} passed={summary.passed} failed={summary.failed}")
    for failure in summary.failures:
        print(f"- {failure.rule_id}: {failure.message}")


def main() -> int:
    summary = run_rule_tests()
    _print_summary(summary)
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
