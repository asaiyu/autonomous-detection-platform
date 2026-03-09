# Solutions Agent

The Solutions Agent closes detection gaps between attack findings and SIEM detections.

## Inputs
- Findings (from Attack Agent runs)
- SIEM alerts and events
- Current ruleset

## Outputs
- Coverage evaluation per finding
- Rule proposals (YAML)
- Replay validation (PASS/FAIL) and metrics
- Coverage snapshot updates (before/after)

## Workflow (v1)
For each finding:
1. Determine expected observable indicators + required telemetry
2. Query SIEM for related alerts/events in the finding time window
3. Assign coverage state:
   - COVERED, PARTIALLY_COVERED, NOT_COVERED, NOT_OBSERVABLE
4. If NOT_COVERED or PARTIALLY_COVERED:
   - generate deterministic rule proposal referencing canonical fields
   - run replay validation (docs/14_replay_engine.md)
   - record proposal + validation results (docs/17_coverage_telemetry.md)
5. If replay PASS:
   - mark proposal VALIDATED (MVP)
   - optional: auto-merge into ruleset (post-MVP)

## Constraints
- Final detection must be deterministic (rule-based).
- LLM/ML may assist generation, but results must be reproducible and testable.
