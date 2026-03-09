from __future__ import annotations

from fastapi.testclient import TestClient


def test_alert_triage_creates_case(client: TestClient) -> None:
    replay_payload = {
        "dataset_id": "juice_shop_local_v1",
        "ruleset_id": "default",
        "mode": "full_evaluation",
    }
    replay_response = client.post("/api/replay", json=replay_payload)
    assert replay_response.status_code == 200

    alerts_response = client.get("/api/alerts", params={"limit": 1})
    assert alerts_response.status_code == 200
    alerts_body = alerts_response.json()
    assert alerts_body["count"] >= 1
    alert_id = alerts_body["items"][0]["alert_id"]

    triage_response = client.post(
        f"/api/alerts/{alert_id}/triage",
        json={"analyst_notes": "Reviewed by analyst"},
    )
    assert triage_response.status_code == 200
    triage_body = triage_response.json()
    assert triage_body["case_id"]
    assert triage_body["triage_json"]["triage_summary"]
    assert isinstance(triage_body["triage_json"]["citations"], list)

    alert_case_response = client.get(f"/api/alerts/{alert_id}/case")
    assert alert_case_response.status_code == 200
    assert alert_case_response.json()["case_id"] == triage_body["case_id"]

    cases_response = client.get("/api/cases", params={"alert_id": alert_id})
    assert cases_response.status_code == 200
    assert cases_response.json()["count"] >= 1


def test_audit_exports_snapshot_diff_and_run_report(client: TestClient) -> None:
    replay_payload = {
        "dataset_id": "juice_shop_local_v1",
        "ruleset_id": "default",
        "mode": "full_evaluation",
    }
    replay_response = client.post("/api/replay", json=replay_payload)
    assert replay_response.status_code == 200

    snapshot_response = client.get(
        "/api/audit/coverage/snapshot",
        params={"dataset_id": "juice_shop_local_v1", "ruleset_id": "default"},
    )
    assert snapshot_response.status_code == 200
    snapshot_body = snapshot_response.json()
    assert snapshot_body["snapshot_id"]
    assert isinstance(snapshot_body["metrics_json"], dict)

    diff_response = client.get(
        "/api/audit/coverage/diff",
        params={
            "dataset_id": "juice_shop_local_v1",
            "from_ruleset": "default",
            "to_ruleset": "default",
        },
    )
    assert diff_response.status_code == 200
    assert "coverage_rate_delta" in diff_response.json()

    runs_response = client.get("/api/runs", params={"limit": 1})
    assert runs_response.status_code == 200
    runs_body = runs_response.json()
    assert runs_body["count"] >= 1
    run_id = runs_body["items"][0]["run_id"]

    report_response = client.get(f"/api/audit/runs/{run_id}/report")
    assert report_response.status_code == 200
    report_body = report_response.json()
    assert report_body["run_id"] == run_id
    assert isinstance(report_body["findings"], list)


def test_mcp_wrappers_for_search_and_rule_proposal(client: TestClient) -> None:
    ingest_payload = {
        "source_type": "http",
        "timestamp": "2026-03-06T10:00:00Z",
        "raw_event": {
            "method": "GET",
            "url": "https://app.local/login",
            "status_code": 200,
        },
    }
    ingest_response = client.post("/api/ingest/event", json=ingest_payload)
    assert ingest_response.status_code == 201

    search_events_response = client.post(
        "/api/mcp/search_events",
        json={"query": "login", "limit": 10},
    )
    assert search_events_response.status_code == 200
    assert search_events_response.json()["count"] >= 1

    proposal_response = client.post(
        "/api/mcp/create_rule_proposal",
        json={
            "title": "MCP Rule Proposal",
            "rule_id": "mcp_rule_proposal",
            "rule_version": 1,
            "rule_yaml": "id: mcp_rule_proposal",
            "rationale": "Created via MCP wrapper",
        },
    )
    assert proposal_response.status_code == 200
    proposal_body = proposal_response.json()
    assert proposal_body["proposal_id"]
