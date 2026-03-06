# autonomous-detection-platform

MVP scaffold for an autonomous detection platform with:
- FastAPI backend (`/api/health` + modular stub routers)
- PostgreSQL + SQLAlchemy + Alembic
- Celery worker skeleton (Redis broker/backend)
- Next.js TypeScript frontend skeleton
- Docker Compose stack (`api`, `worker`, `postgres`, `redis`)

## Docs
- Architecture/schema references are in `docs/`.
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
Health smoke test:
```bash
cd backend
pytest -q
```
