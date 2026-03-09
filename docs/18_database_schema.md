# Database Schema (Minimal MVP)

This is the minimal relational schema to support ingestion, alerts, and coverage telemetry.

## Core tables

### events
- event_id (pk uuid)
- timestamp (timestamptz)
- source_type (text)
- canonical_event_json (jsonb)
- raw_event_json (jsonb nullable)
- dataset_id (text nullable)
- run_id (uuid nullable)

### alerts
- alert_id (pk uuid)
- rule_id (text)
- rule_version (int)
- severity (text)
- title (text)
- category (text)
- type (text)
- status (text)
- confidence (float)
- created_at (timestamptz)
- evidence_event_ids (jsonb array)
- evidence_json (jsonb)
- tags (jsonb array)

### cases (optional in MVP, can be minimal)
- case_id (pk uuid)
- alert_id (fk)
- notes_markdown (text)
- triage_json (jsonb)

## Coverage / improvement tables

### attack_runs
- run_id (pk uuid)
- attack_source (text)
- dataset_id (text)
- target (text)
- start_time, end_time
- config_json (jsonb)
- config_hash (text)
- status (text)
- summary (text)

### findings
- finding_id (pk uuid)
- run_id (fk)
- finding_type (text)
- title (text)
- severity (text)
- technique (text nullable)
- entrypoint_json (jsonb)
- proof_json (jsonb)
- occurred_at (timestamptz)
- tags_json (jsonb)

### coverage_evaluations
- evaluation_id (pk uuid)
- finding_id (fk)
- run_id (fk)
- evaluated_at (timestamptz)
- coverage_state (text)
- window_start, window_end
- related_event_ids_json (jsonb)
- related_alert_ids_json (jsonb)
- missing_telemetry_json (jsonb)
- notes (text)

### rule_proposals
- proposal_id (pk uuid)
- evaluation_id (fk)
- rule_id (text)
- rule_version (int)
- proposal_status (text)
- rule_yaml (text)
- rationale (text)
- created_at (timestamptz)
- created_by (text)
- references_json (jsonb)
- risk_notes (text)

### replay_validations
- validation_id (pk uuid)
- proposal_id (fk)
- attack_dataset_id (text)
- baseline_dataset_id (text)
- replay_started_at, replay_finished_at
- results_json (jsonb)
- verdict (text)
- report (text)

### rulesets
- ruleset_id (text pk)         # e.g., "ruleset_v1" or git SHA
- created_at (timestamptz)
- note (text)

### coverage_snapshots
- snapshot_id (pk uuid)
- dataset_id (text)
- ruleset_id (text fk)
- computed_at (timestamptz)
- metrics_json (jsonb)
