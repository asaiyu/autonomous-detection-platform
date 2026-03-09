# Autonomous Detection Engineering Platform

This project builds a **self-improving detection engineering loop**.

## Agents

### Attack Agent
Generates adversarial activity and produces:
- **Findings** (ground truth of what attack was proven)
- **Telemetry Events** (canonical events that SIEM can ingest)

Attack sources (v1):
- Shannon (web exploit pentesting)
- Synthetic Scenario Generator (endpoint/network/DNS scenarios)

### SIEM Agent
- Ingest raw telemetry
- Normalize into canonical schema
- Run deterministic rules to create alerts
- Store evidence bundles and case notes
- Serve investigation APIs for UI

### Solutions Agent
- Compare Findings to SIEM alerts
- Identify gaps (NOT_COVERED / PARTIALLY_COVERED / NOT_OBSERVABLE)
- Propose deterministic detection rules
- Validate rules by replay (TP/FP)
- Record the change so coverage improvement can be showcased

## Why this exists
Most teams ship code continuously but test security periodically. This platform continuously measures and improves detection coverage.
