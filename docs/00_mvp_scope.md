# MVP Scope Definition

This document defines the **Minimum Viable Product (MVP)** scope for the Autonomous Detection Engineering Platform.

The MVP demonstrates a closed security improvement loop:

**Attack → Telemetry → Detection → Gap Analysis → Rule Generation → Replay Validation → Improved Coverage**

The MVP prioritizes:
- Simplicity
- Deterministic behavior
- Reproducibility
- Clear, demo-friendly evidence of coverage improvement

Non-goals in v1:
- RBAC / multi-tenancy
- Advanced ML anomaly detection as primary detection
- Distributed scaling and HA clusters
- Complex multi-stage attack graphs

## MVP Success Criteria

The MVP is successful when it can show, on a **fixed dataset**:

- Initial coverage (ruleset V1) is measured and stored
- Solutions Agent proposes one or more deterministic rules
- Replay validation proves the new rules detect the attack and keep false positives low
- Coverage improves (ruleset V2) and the improvement is displayed in the UI with drill-down evidence

Example demo outcome:
- Coverage on dataset `juice_shop_local_v1` improves from **12% → 75%**
- Each improvement is traceable: **Finding → Gap → Proposed Rule → Replay PASS → Merged Rule**
