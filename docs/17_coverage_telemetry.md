# Coverage Telemetry & Record Keeping

The platform must keep durable records showing how detection coverage improved over time.

It must be possible to answer:
- What attack was generated?
- Was it detected?
- If not, what rule was created?
- Did replay validate the rule?
- Did coverage improve on the same dataset?

Tracked entities:
- attack_runs
- findings
- coverage_evaluations
- rule_proposals
- replay_validations
- coverage_snapshots (dataset + ruleset metrics)

## Coverage Metrics
For a dataset:
- total_findings
- covered_count
- partially_covered_count
- not_covered_count
- not_observable_count
- coverage_rate = covered_count / total_findings
- effective_coverage_rate = (covered_count + partially_covered_count) / total_findings

## Required UI
- Coverage dashboard (before/after on same dataset)
- Run detail (Finding → Gap → Proposal → Replay PASS/FAIL)
- Rule impact page (which findings it closed)
