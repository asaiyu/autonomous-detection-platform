# Coverage Metrics

This document defines how the platform measures and reports detection coverage.

## Core metrics (dataset-scoped)

Given a dataset D with findings F:

- total_findings = |F|
- covered_findings = findings with at least one supporting alert with adequate evidence
- partially_covered_findings = alert exists but missing key evidence or wrong severity
- not_covered_findings = no alert exists
- not_observable_findings = missing telemetry sources required to detect

### coverage_rate
coverage_rate = covered_findings / total_findings

### effective_coverage_rate
effective_coverage_rate = (covered_findings + partially_covered_findings) / total_findings

## Operational metrics

### rule_validation_pass_rate
PASS proposals / total proposals

### gap_close_rate
MERGED proposals / NOT_COVERED findings (over interval)

### detection_latency (optional)
alert.created_at - finding.occurred_at

## Visualization recommendations
- Coverage over time per dataset (by ruleset versions)
- Coverage breakdown by finding_type (SQLI, SSRF, AUTH_BYPASS, etc.)
- Rules responsible for biggest improvements
