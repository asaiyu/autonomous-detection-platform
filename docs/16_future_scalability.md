# Future Scalability (Post-MVP)

This document lists future enhancements without implementing them in v1.

## Data + Search
- Add OpenSearch for fast event/alert search and aggregations
- Keep PostgreSQL as system of record, index asynchronously

## Detection
- Threshold rules (N events in M minutes)
- 3+ stage sequences and correlation
- Sigma import/export compatibility

## Platform
- Multi-tenant isolation
- RBAC
- Model governance + audit trails
- Horizontal scaling (workers, rule engine)

## Operations
- Full OpenTelemetry pipeline
- Rate limiting, quotas, and backpressure
- Hardening and secure defaults
