from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_create_rule_proposal_mode(client: TestClient) -> None:
    payload = {
        "mode": "proposal",
        "title": "Suspicious test rule",
        "rule_id": "test_rule_proposal",
        "rule_version": 1,
        "rule_yaml": "id: test_rule_proposal\nname: Test\nseverity: low\ndetect: {type: single, where: {field: source.type, op: equals, value: dns}}\noutput: {alert_title: Test, alert_category: network, alert_type: test, confidence: 0.5, default_status: open}\n",
        "rationale": "test rationale",
    }

    response = client.post("/api/rules", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["proposal_id"]


def test_create_rule_ruleset_mode_writes_rule_file(
    client: TestClient,
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("RULES_DIR", str(tmp_path))

    payload = {
        "mode": "ruleset",
        "ruleset_id": "ruleset_test_v1",
        "ruleset_note": "test ruleset update",
        "title": "Apply test rule",
        "rule_id": "test_rule_ruleset",
        "rule_version": 3,
        "rule_yaml": (
            "id: test_rule_ruleset\n"
            "name: Test Ruleset Rule\n"
            "severity: medium\n"
            "detect:\n"
            "  type: single\n"
            "  where:\n"
            "    field: source.type\n"
            "    op: equals\n"
            "    value: dns\n"
            "output:\n"
            "  alert_title: Test Rule\n"
            "  alert_category: network\n"
            "  alert_type: test\n"
            "  confidence: 0.7\n"
            "  default_status: open\n"
        ),
        "rationale": "apply rule to active ruleset",
    }

    response = client.post("/api/rules", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "applied"
    assert body["ruleset_id"] == "ruleset_test_v1"

    written = tmp_path / "test_rule_ruleset.yaml"
    assert written.exists()
    contents = written.read_text(encoding="utf-8")
    assert "id: test_rule_ruleset" in contents
