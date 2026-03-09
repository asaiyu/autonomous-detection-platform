# Replay Engine Specification

The Replay Engine evaluates detection rules against historical telemetry datasets.

Primary purposes:
1. Validate that a proposed rule detects the attack it was designed for (TP)
2. Validate that it does not generate excessive false positives on baseline traffic (FP)
3. Produce deterministic, reproducible results

## Inputs
Replay requires:
- dataset_id
- ruleset_id
- mode: attack_validation | baseline_validation | full_evaluation

## Execution
- Events are processed in timestamp ascending order.
- No randomness is allowed.
- Replay produces alert records as if the rules were running live.

## Outputs
Replay returns:
- alerts_generated
- attack_tp_count
- baseline_fp_count
- coverage_rate (when findings exist)
- sample_alert_ids
- sample_event_ids
- timings (started/finished)

Example output:
```json
{
  "dataset_id": "juice_shop_local_v1",
  "ruleset_id": "ruleset_v2",
  "attack_tp_count": 6,
  "baseline_fp_count": 1,
  "coverage_rate": 0.75
}
```

## PASS/FAIL Criteria (Rule Proposal Validation)
Default thresholds:
- allowed_fp_threshold = 2

PASS if:
- attack_tp_count >= 1 AND baseline_fp_count <= allowed_fp_threshold

FAIL if:
- attack_tp_count == 0 OR baseline_fp_count > allowed_fp_threshold

## Evidence Bundles
Every alert must store:
- triggering event_ids
- extracted fields per rule.evidence.include_fields
