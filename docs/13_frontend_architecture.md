# Frontend Architecture (MVP)

Frontend is a Next.js (TypeScript) application.

## Pages (MVP)
- /coverage
  - coverage snapshot chart + deltas
- /runs
  - list attack runs
- /runs/[run_id]
  - findings + coverage state + proposed rules + validation results
- /alerts
  - alert list with filtering
- /alerts/[alert_id]
  - evidence bundle and triage/case notes
- /rules
  - rule library and proposals

## Data fetching
- TanStack Query for caching and pagination
- SSE or polling for near-real-time updates (MVP can use polling)

## UI components
- shadcn/ui for consistent layout and tables
- Markdown renderer for rule YAML and reports
