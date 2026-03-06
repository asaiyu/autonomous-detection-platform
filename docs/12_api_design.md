# API Design (MVP)

The API is served by FastAPI and provides endpoints for:
- ingestion
- querying events/alerts
- running replays
- managing datasets/rulesets
- coverage dashboards

All endpoints return JSON. Bulk ingestion accepts NDJSON.

## Core Endpoints

### Health
- GET /api/health

### Ingest
- POST /api/ingest/event
  - body: { raw_event, source_type, timestamp? }
- POST /api/ingest/bulk (NDJSON)
  - each line: { raw_event, source_type, timestamp? }

### Events
- GET /api/events?query=&start=&end=&limit=
- GET /api/events/{event_id}

### Alerts
- GET /api/alerts?query=&start=&end=&limit=
- GET /api/alerts/{alert_id}
- GET /api/alerts/{alert_id}/evidence

### Rules
- GET /api/rules
- GET /api/rules/{rule_id}
- POST /api/rules (create proposal or add rule depending on mode)

### Replay
- POST /api/replay
  - body: { dataset_id, ruleset_id, mode }

### Attack Runs / Findings
- GET /api/runs
- GET /api/runs/{run_id}
- GET /api/runs/{run_id}/findings

### Coverage
- GET /api/coverage/snapshots?dataset_id=
- GET /api/coverage/diff?dataset_id=&from_ruleset=&to_ruleset=
