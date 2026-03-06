# Audit Artifacts & Showcase Exports

The platform must produce artifacts for demos and verification.

## Export types

### Coverage Snapshot
A point-in-time summary for (dataset_id, ruleset_id).
Includes:
- metrics_json
- top gaps (by severity/type)
- counts of rules merged/validated

### Coverage Diff (Before vs After)
Compares two snapshots on the same dataset:
- coverage_rate delta
- gaps closed count
- list of rules responsible for improvements
- replay validation evidence references

### Run Report
For a run_id:
- run metadata
- findings list
- coverage evaluations
- rule proposals + replay validation verdicts

## Formats
- JSON export for machine processing
- Markdown export for human-readable demo report

## Acceptance criteria
- No fabricated data
- References use stable IDs (finding_id, proposal_id, alert_id, event_id)
