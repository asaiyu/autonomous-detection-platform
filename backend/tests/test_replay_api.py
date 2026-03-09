from __future__ import annotations

from fastapi.testclient import TestClient


def test_replay_full_evaluation_returns_expected_metrics(client: TestClient) -> None:
    payload = {
        "dataset_id": "juice_shop_local_v1",
        "ruleset_id": "default",
        "mode": "full_evaluation",
    }

    response = client.post("/api/replay", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["alerts_generated"] == 2
    assert body["attack_tp_count"] == 2
    assert body["baseline_fp_count"] == 0
    assert body["coverage_rate"] == 1.0
    assert body["verdict"] == "PASS"


def test_replay_baseline_only_fails_without_attack_tp(client: TestClient) -> None:
    payload = {
        "dataset_id": "juice_shop_local_v1",
        "ruleset_id": "default",
        "mode": "baseline_validation",
    }

    response = client.post("/api/replay", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["attack_tp_count"] == 0
    assert body["verdict"] == "FAIL"
