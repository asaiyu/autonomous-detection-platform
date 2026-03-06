# Repository Structure

```text
autonomous-detection-platform/
├── .env.example
├── .gitignore
├── README.md
├── REPO_STRUCTURE.md
├── docker-compose.yml
├── docs/
│   ├── 08_event_schema.md
│   └── 18_database_schema.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 0001_create_initial_tables.py
│   │       └── 0002_event_json_cols.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── alerts.py
│   │   │       ├── coverage.py
│   │   │       ├── events.py
│   │   │       ├── health.py
│   │   │       ├── ingest.py
│   │   │       ├── replay.py
│   │   │       ├── rules.py
│   │   │       └── runs.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── event.py
│   │   │   └── ingest.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── event_normalization.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── alert.py
│   │   │   ├── attack_run.py
│   │   │   ├── coverage_evaluation.py
│   │   │   ├── coverage_snapshot.py
│   │   │   ├── event.py
│   │   │   ├── finding.py
│   │   │   ├── replay_validation.py
│   │   │   ├── rule_proposal.py
│   │   │   └── ruleset.py
│   │   └── worker/
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── celery_app.py
│   │       └── tasks/
│   │           ├── __init__.py
│   │           ├── coverage_tasks.py
│   │           ├── ingest_tasks.py
│   │           ├── replay_tasks.py
│   │           └── triage_tasks.py
│   └── tests/
│       └── test_health.py
└── frontend/
    ├── Dockerfile
    ├── next-env.d.ts
    ├── next.config.mjs
    ├── package.json
    ├── tsconfig.json
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── alerts/
    │   │   └── page.tsx
    │   ├── coverage/
    │   │   └── page.tsx
    │   ├── rules/
    │   │   └── page.tsx
    │   └── runs/
    │       └── page.tsx
    └── lib/
        └── api.ts
```
