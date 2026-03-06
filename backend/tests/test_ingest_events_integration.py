from __future__ import annotations

import json

from fastapi.testclient import TestClient


def test_ingest_event_and_fetch_by_id(client: TestClient) -> None:
    ingest_payload = {
        "source_type": "dns",
        "timestamp": "2026-03-06T12:00:00Z",
        "raw_event": {
            "query": "example.com",
            "qtype": "A",
            "rcode": "NOERROR",
            "src_ip": "10.0.0.5",
            "dst_ip": "8.8.8.8",
        },
    }

    ingest_response = client.post("/api/ingest/event", json=ingest_payload)
    assert ingest_response.status_code == 201

    body = ingest_response.json()
    event_id = body["event_id"]
    canonical = body["canonical_event"]

    assert canonical["source"]["type"] == "dns"
    assert canonical["event"]["category"] == "network"
    assert canonical["event"]["type"] == "dns_query"
    assert canonical["dns"]["query"] == "example.com"

    fetched_response = client.get(f"/api/events/{event_id}")
    assert fetched_response.status_code == 200

    fetched = fetched_response.json()
    assert fetched["event_id"] == event_id
    assert fetched["source_type"] == "dns"
    assert fetched["raw_event_json"]["query"] == "example.com"


def test_bulk_ingest_and_event_queries(client: TestClient) -> None:
    bulk_lines = [
        json.dumps(
            {
                "source_type": "http",
                "timestamp": "2026-03-06T10:00:00Z",
                "raw_event": {
                    "method": "GET",
                    "url": "https://app.local/login",
                    "status_code": 200,
                    "user_agent": "curl/8.0",
                },
            }
        ),
        "not-json",
        json.dumps(
            {
                "source_type": "dns",
                "timestamp": "2026-03-06T11:00:00Z",
                "raw_event": {
                    "query": "internal.local",
                    "record_type": "AAAA",
                },
            }
        ),
    ]

    bulk_response = client.post(
        "/api/ingest/bulk",
        content="\n".join(bulk_lines),
        headers={"Content-Type": "application/x-ndjson"},
    )
    assert bulk_response.status_code == 200

    bulk = bulk_response.json()
    assert bulk["ingested"] == 2
    assert bulk["error_count"] == 1
    assert bulk["errors"][0]["line_number"] == 2

    dns_events_response = client.get("/api/events", params={"source_type": "dns", "limit": 10})
    assert dns_events_response.status_code == 200
    dns_events = dns_events_response.json()
    assert dns_events["count"] == 1
    assert dns_events["items"][0]["source_type"] == "dns"

    query_response = client.get("/api/events", params={"q": "login", "limit": 10})
    assert query_response.status_code == 200
    queried = query_response.json()
    assert queried["count"] == 1
    assert queried["items"][0]["source_type"] == "http"

    window_response = client.get(
        "/api/events",
        params={
            "start_timestamp": "2026-03-06T09:59:00Z",
            "end_timestamp": "2026-03-06T10:01:00Z",
            "limit": 10,
        },
    )
    assert window_response.status_code == 200
    windowed = window_response.json()
    assert windowed["count"] == 1
    assert windowed["items"][0]["source_type"] == "http"
