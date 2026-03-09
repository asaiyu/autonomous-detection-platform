# Attack Agent

The Attack Agent generates adversarial activity and emits structured outputs to feed the SIEM and Solutions Agent.

## Sources (v1)

### A) Shannon Adapter (Web Exploits)
- Runs Shannon against a target web application
- Produces **Findings** (proven exploitable issues)
- Produces **HTTP telemetry** (and any emitted DNS/firewall telemetry if available in environment)

### B) Synthetic Scenario Generator (Endpoint/Network/DNS)
- Generates realistic telemetry for:
  - Windows process/auth events
  - macOS auth/process events
  - DNS queries
  - Firewall egress/ingress events
- Produces Findings as ground truth labels

## Outputs

### Findings
- finding_id (uuid)
- run_id (uuid)
- finding_type (SQLI, SSRF, AUTH_BYPASS, PASSWORD_SPRAY, etc.)
- severity
- entrypoint (method/path or host/process)
- proof/evidence references
- occurred_at timestamp

### Telemetry Events
- Raw events (optional)
- Canonical events (required): must match docs/08_event_schema.md

## Run Metadata
Every run must record:
- run_id, dataset_id, attack_source
- config + config_hash
- start/end times, status
