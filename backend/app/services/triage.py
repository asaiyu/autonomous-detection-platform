from __future__ import annotations

from typing import Any, Optional

from app.models.alert import Alert
from app.schemas.case import TriageOutput


def generate_triage_output(alert: Alert, analyst_notes: Optional[str] = None) -> TriageOutput:
    evidence_ids = alert.evidence_event_ids or []
    evidence_json = alert.evidence_json or {}
    citations = _build_citations(evidence_ids=evidence_ids, evidence_json=evidence_json)

    if not evidence_ids and not evidence_json:
        summary = (
            f"Alert {alert.id} has insufficient evidence payloads. Additional telemetry should be collected "
            "before concluding root cause."
        )
    else:
        summary = (
            f"Alert {alert.id} fired rule {alert.rule_id or 'unknown_rule'} with severity {alert.severity}. "
            f"Evidence references {len(evidence_ids)} event(s) and {len(_collect_evidence_fields(evidence_json))} field(s)."
        )

    likely_technique = _infer_technique(alert.category, alert.alert_type, alert.rule_id)
    recommended_actions = _recommended_actions(alert.category, alert.severity, not bool(citations))
    case_notes = _build_case_notes(summary=summary, citations=citations, analyst_notes=analyst_notes)

    return TriageOutput(
        triage_summary=summary,
        likely_technique=likely_technique,
        recommended_actions=recommended_actions,
        case_notes=case_notes,
        citations=citations,
    )


def _build_citations(evidence_ids: list[str], evidence_json: dict[str, Any]) -> list[str]:
    citations: list[str] = []
    for event_id in evidence_ids[:20]:
        citations.append(f"event_id:{event_id}")

    for field in _collect_evidence_fields(evidence_json)[:20]:
        citations.append(f"field:{field}")

    return citations


def _collect_evidence_fields(evidence_json: Any, parent: str = "") -> list[str]:
    fields: list[str] = []
    if isinstance(evidence_json, dict):
        for key, value in evidence_json.items():
            path = f"{parent}.{key}" if parent else key
            if isinstance(value, dict):
                fields.extend(_collect_evidence_fields(value, path))
            else:
                fields.append(path)
    return fields


def _infer_technique(category: Optional[str], alert_type: Optional[str], rule_id: Optional[str]) -> Optional[str]:
    value = " ".join(
        item.lower()
        for item in [category or "", alert_type or "", rule_id or ""]
        if item
    )
    if "powershell" in value or "execution" in value:
        return "T1059 Command and Scripting Interpreter"
    if "dns" in value or "egress" in value or "network" in value:
        return "T1071 Application Layer Protocol"
    if "credential" in value or "login" in value:
        return "T1110 Brute Force"
    return None


def _recommended_actions(category: Optional[str], severity: str, insufficient_evidence: bool) -> list[str]:
    actions = [
        "Validate the alert timeline against raw and canonical telemetry.",
        "Confirm whether the triggering behavior is expected for the affected asset.",
    ]

    if (category or "").lower() == "network":
        actions.append("Review destination IP/domain reputation and related outbound connections.")
    if severity.lower() in {"high", "critical"}:
        actions.append("Escalate to incident response and isolate the impacted host if maliciousness is confirmed.")
    if insufficient_evidence:
        actions.append("Collect additional endpoint/network telemetry for a higher-confidence determination.")
    return actions


def _build_case_notes(summary: str, citations: list[str], analyst_notes: Optional[str]) -> str:
    lines = [
        "# Triage Summary",
        summary,
        "",
        "## Citations",
    ]

    if citations:
        lines.extend([f"- {citation}" for citation in citations])
    else:
        lines.append("- No citations available.")

    if analyst_notes:
        lines.extend(["", "## Analyst Notes", analyst_notes])

    return "\n".join(lines)
