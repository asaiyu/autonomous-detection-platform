# Data Pipeline

This document describes the MVP data flow from telemetry ingestion to alerts and coverage metrics.

## 1) Ingestion
- Input formats:
  - JSON (single event)
  - NDJSON (bulk events)
- Each ingested record may be:
  - raw_event (source-specific)
  - canonical_event (normalized)

## 2) Normalization
- Normalizers map raw payloads into canonical schema (`docs/08_event_schema.md`)
- Normalization is deterministic and versioned (store `normalizer_version`)

## 3) Storage
- Store canonical events in PostgreSQL
- Store raw payload as JSONB for evidence/repro (optional but recommended)

## 4) Detection
- Rule engine evaluates events in timestamp order
- Emits alerts with evidence bundles

## 5) Triage (post-detection)
- AI triage generates:
  - summary
  - suspected technique
  - recommended next steps
  - saves case notes

## 6) Coverage loop
- Attack Agent produces Findings
- Solutions Agent evaluates coverage and proposes rules
- Replay engine validates proposals
- Coverage telemetry captures before/after metrics
