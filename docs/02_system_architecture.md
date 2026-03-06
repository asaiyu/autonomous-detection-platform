# System Architecture

High-level flow:

1. **Attack Agent** produces Findings + Telemetry
2. **SIEM Agent** ingests Telemetry and produces Alerts
3. **Solutions Agent** compares Findings ↔ Alerts and proposes rules
4. **Replay Engine** validates new rules on a fixed dataset
5. **Coverage Telemetry** shows before/after improvement

## Deployment Shape (MVP)

- Frontend: Next.js (TypeScript)
- API: FastAPI (Python)
- Workers: Celery or RQ (Python) + Redis
- Database: PostgreSQL
- Optional search: OpenSearch (future)

## Logical Diagram

                    +--------------------+
                    |    Next.js UI      |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    |    FastAPI API     |
                    +---------+----------+
                              |
      +-----------------------+------------------------+
      |                        |                       |
      v                        v                       v
+-------------+        +----------------+      +-----------------+
| SIEM Agent  |        | Attack Agent   |      | Solutions Agent |
+-------------+        +----------------+      +-----------------+
      |
      v
+-----------------+
| Replay Engine    |
+-----------------+

Shared infra: PostgreSQL, Redis
