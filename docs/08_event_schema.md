# Canonical Event Schema

All telemetry ingested by the SIEM must be normalized into a canonical schema.
Rules operate only on canonical fields.

## Event Envelope (required)

Every canonical event MUST include:

- event_id (string UUID)
- timestamp (ISO8601 UTC)
- source.type (string)
- event.category (string) and event.type (string) when applicable

Recommended: keep the original raw payload for evidence.

### Suggested storage shape (DB)
- raw_event_json (original payload)
- canonical_event_json (normalized payload)

## Canonical Structure (top-level)

```json
{
  "event_id": "uuid",
  "timestamp": "2026-03-04T18:21:03Z",
  "source": { "type": "dns", "product": "bind", "component": "resolver" },
  "host": { "hostname": "mac-01", "ip": "10.0.0.8", "os": "macos" },
  "user": { "name": "alice", "domain": "corp" },
  "process": {
    "name": "powershell.exe",
    "path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
    "command_line": "powershell -encodedcommand ...",
    "pid": 1234,
    "parent_name": "winword.exe",
    "parent_pid": 456
  },
  "network": {
    "src_ip": "10.0.0.8",
    "src_port": 51515,
    "dst_ip": "8.8.8.8",
    "dst_port": 53,
    "protocol": "udp",
    "direction": "outbound",
    "action": "allow"
  },
  "dns": { "query": "example.com", "record_type": "A", "rcode": "NOERROR", "response": "93.184.216.34" },
  "http": { "method": "GET", "path": "/login", "query": "u=a", "status_code": 200, "user_agent": "Mozilla/5.0" },
  "file": { "path": "/tmp/x", "name": "x", "hash": "sha256:...", "action": "create" },
  "event": { "category": "authentication", "type": "login_failure", "severity": "medium", "message": "Bad password" }
}
```

Not all objects are populated for every event.
