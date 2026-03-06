# SIEM Agent Architecture

The SIEM Agent is a rule-based detection system with post-detection AI triage.

## Responsibilities
- Ingest raw telemetry (HTTP, DNS, firewall, Windows, macOS)
- Normalize raw events into canonical events
- Store raw + canonical events
- Evaluate deterministic rules (docs/09_detection_rules.md)
- Create alerts with evidence bundles
- Provide investigation APIs (events, alerts, cases)
- Store case notes and AI triage outputs

## Pipeline
Raw Event → Normalize → Store Event → Evaluate Rules → Create Alert → Persist Evidence → (Optional) AI Triage → Case Notes

## Key Modules (MVP)
- Ingest API (bulk NDJSON and single events)
- Normalization library (source-specific mappers)
- Rule engine (single + 2-stage sequence)
- Alert store and evidence extractor
- Replay engine interface (docs/14_replay_engine.md)
