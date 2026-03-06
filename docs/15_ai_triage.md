# AI Triage (Post-detection)

AI triage runs after deterministic detection creates an alert.

## Goals
- Summarize what happened and why the rule fired
- Cite evidence fields from the alert evidence bundle
- Suggest next investigation steps
- Save case notes that are editable by the analyst

## Inputs
- Alert record (rule_id, severity, timestamps)
- Evidence bundle (canonical fields + raw snippets when available)
- Optional: related events around the time window

## Outputs
- triage_summary (short narrative)
- likely_technique (optional label)
- recommended_actions (list)
- case_notes (markdown)
- citations (references to event_ids / evidence fields)

## Constraints
- Must not fabricate evidence
- Must cite event_ids and fields used
- If evidence is insufficient, say so and recommend additional telemetry
