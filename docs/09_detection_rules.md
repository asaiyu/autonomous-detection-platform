# Detection Rules Specification (v1)

Rules are deterministic YAML files stored under:

```
rules/<rule_id>.yaml
```

All rule conditions reference fields from the Canonical Event Schema (`docs/08_event_schema.md`).

## Design Goals
- Deterministic, replayable detections
- Clear evidence capture (why a rule fired)
- Testability (fixtures + expected alerts)

Non-goals in v1:
- ML detections as primary detection mechanism
- 3+ stage sequences / graph logic
- Complex aggregations (thresholds) beyond v1 sequence

---

## 1) Rule YAML Format

### Required fields
```yaml
id: suspicious_dns_outbound_connect
name: "Suspicious DNS followed by outbound connect"
description: "Detects DNS query to suspicious domain and outbound connection shortly after."
severity: medium               # low|medium|high|critical
enabled: true
log_sources:
  - dns
  - firewall
tags: [dns, egress]
version: 1
created_at: "2026-03-04"
author: "manual"
references: []
```

### Detection block (required)
```yaml
detect:
  type: single | sequence
  ...
```

### Output block (required)
```yaml
output:
  alert_title: "Suspicious DNS + outbound connect"
  alert_category: "network"
  alert_type: "suspicious_egress"
  confidence: 0.7
  default_status: "open"
```

### Evidence block (optional but recommended)
```yaml
evidence:
  include_fields:
    - timestamp
    - source.type
    - host.hostname
    - user.name
    - process.name
    - process.command_line
    - network.src_ip
    - network.dst_ip
    - dns.query
    - http.method
    - http.path
```

---

## 2) Field Addressing
Conditions refer to canonical fields by dot path (e.g., `process.command_line`). Missing fields evaluate as null.

---

## 3) Operators (v1)

### String
- equals, iequals
- contains, icontains
- regex

### Numeric
- gt, gte, lt, lte, between

### Set
- in, nin

### Existence
- exists, not_exists

### Boolean composition
- all (AND)
- any (OR)
- not (negation)

---

## 4) Single-event rules

```yaml
detect:
  type: single
  where:
    all:
      - field: source.type
        op: equals
        value: windows
      - field: process.name
        op: iequals
        value: powershell.exe
      - field: process.command_line
        op: icontains
        value: "-encodedcommand"
```

Optional dedupe:
```yaml
detect:
  type: single
  where: ...
  dedupe:
    key_fields: [host.hostname, user.name]
    window_seconds: 900
```

---

## 5) Sequence rules (v1 limited correlation)

Supports exactly **two stages** with a time window and join keys.

```yaml
detect:
  type: sequence
  window_seconds: 300
  join_keys: [host.hostname, user.name]
  stages:
    - id: stage1
      where: { ... }
    - id: stage2
      where: { ... }
```

Fires when stage2 occurs after stage1 within `window_seconds` and all join keys match.

---

## 6) Rule Testing

Each rule should have deterministic tests:

```
tests/rules/<rule_id>/events.ndjson
tests/rules/<rule_id>/expected_alerts.json
```

`events.ndjson`: newline-delimited canonical events.
`expected_alerts.json`: minimal assertions:
- should_fire (bool)
- expected_count (int)
- evidence_event_ids_contains (list)

---

## 7) Acceptance Criteria (v1)
- Load YAML rules in `rules/`
- Evaluate single and two-stage sequence rules deterministically
- Create alerts with evidence bundles
- Run rule tests from `tests/rules/*`
