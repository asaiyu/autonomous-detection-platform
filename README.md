# autonomous-detection-platform

MVP scaffold for an autonomous detection platform with:
- FastAPI backend (`/api/health`, SIEM ingest path, events query APIs)
- PostgreSQL + SQLAlchemy + Alembic
- Celery worker skeleton (Redis broker/backend)
- Next.js TypeScript frontend skeleton
- Docker Compose stack (`api`, `worker`, `postgres`, `redis`)

## Docs
- Architecture/schema references are in `docs/`.
- Canonical event schema: `docs/08_event_schema.md`.
- MVP schema doc: `docs/18_database_schema.md`.
- Expected project layout: `REPO_STRUCTURE.md`.

## Quick Start (Docker)
1. Copy env template:
```bash
cp .env.example .env
```
2. Build and run the stack:
```bash
docker-compose up --build
```
3. Verify health endpoint:
```bash
curl http://localhost:8000/api/health
```
Expected response:
```json
{"status":"ok"}
```

## Backend Local Dev
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Alembic
Run migrations from `backend/`:
```bash
alembic upgrade head
```

## Deterministic Rule Engine (v1)
- Rules are loaded from `rules/*.yaml`.
- Supported operators/composition:
  - `all` / `any` / `not`
  - `equals`, `iequals`, `contains`, `icontains`, `regex`
  - `exists`, `not_exists`
  - `in`, `nin`
  - `gt`, `gte`, `lt`, `lte`, `between`
- Rule types:
  - `single`
  - `sequence` (exactly 2 stages) with `join_keys` + `window_seconds`

## Worker
Start worker from `backend/`:
```bash
python -m app.worker
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```

## Tests
Smoke + integration tests:
```bash
cd backend
pytest -q
```

Run deterministic rule fixtures (`/tests/rules/*`):
```bash
cd backend
python -m app.detection.test_runner
```

## SIEM Ingest API Examples
Single event ingest (`dns`):
```bash
curl -X POST http://localhost:8000/api/ingest/event \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "dns",
    "timestamp": "2026-03-06T12:00:00Z",
    "raw_event": {
      "query": "example.com",
      "qtype": "A",
      "rcode": "NOERROR",
      "src_ip": "10.0.0.10",
      "dst_ip": "8.8.8.8"
    }
  }'
```

Bulk ingest (`NDJSON`):
```bash
cat <<'NDJSON' | curl -X POST http://localhost:8000/api/ingest/bulk \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @-
{"source_type":"http","timestamp":"2026-03-06T10:00:00Z","raw_event":{"method":"GET","url":"https://app.local/login","status_code":200}}
{"source_type":"dns","timestamp":"2026-03-06T10:01:00Z","raw_event":{"query":"internal.local","record_type":"AAAA"}}
NDJSON
```

Query events:
```bash
curl "http://localhost:8000/api/events?source_type=dns&limit=20"
curl "http://localhost:8000/api/events?q=login&start_timestamp=2026-03-06T00:00:00Z&end_timestamp=2026-03-07T00:00:00Z"
curl "http://localhost:8000/api/events/<event_id>"
```

Replay evaluation:
```bash
curl -X POST http://localhost:8000/api/replay \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "juice_shop_local_v1",
    "ruleset_id": "default",
    "mode": "full_evaluation"
  }'
```

## P2 APIs (Triage, Audit, MCP Wrappers)
Generate deterministic triage + case record for an alert:
```bash
curl -X POST http://localhost:8000/api/alerts/<alert_id>/triage \
  -H "Content-Type: application/json" \
  -d '{"analyst_notes":"Validated suspicious outbound pattern"}'
```

Audit artifact exports:
```bash
curl "http://localhost:8000/api/audit/coverage/snapshot?dataset_id=juice_shop_local_v1&ruleset_id=default"
curl "http://localhost:8000/api/audit/coverage/diff?dataset_id=juice_shop_local_v1&from_ruleset=default&to_ruleset=default"
curl "http://localhost:8000/api/audit/runs/<run_id>/report"
```

MCP-style wrappers:
```bash
curl -X POST http://localhost:8000/api/mcp/search_events \
  -H "Content-Type: application/json" \
  -d '{"query":"login","limit":20}'
```
