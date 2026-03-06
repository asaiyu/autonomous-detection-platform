from fastapi import APIRouter

from app.api.routes import alerts, audit, cases, coverage, events, health, ingest, mcp, replay, rules, runs

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(replay.router, prefix="/replay", tags=["replay"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(coverage.router, prefix="/coverage", tags=["coverage"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
