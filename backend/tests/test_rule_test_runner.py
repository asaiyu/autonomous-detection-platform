from __future__ import annotations

from app.detection.test_runner import run_rule_tests


def test_rule_test_runner_passes_fixtures() -> None:
    summary = run_rule_tests()

    assert summary.total >= 2
    assert summary.failed == 0
    assert not summary.failures
