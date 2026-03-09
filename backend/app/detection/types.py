from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class RuleDefinition:
    id: str
    name: str
    description: str
    severity: str
    enabled: bool
    log_sources: list[str]
    tags: list[str]
    version: int
    detect_type: str
    detect: dict[str, Any]
    output: dict[str, Any]
    evidence_fields: list[str]


@dataclass(frozen=True)
class AlertMatch:
    rule_id: str
    rule_version: int
    severity: str
    title: str
    category: str
    alert_type: str
    confidence: float
    status: str
    description: str
    evidence_event_ids: list[str]
    evidence_json: dict[str, Any]
    matched_at: datetime
    source_event_id: Optional[str]


@dataclass(frozen=True)
class ReplayResult:
    dataset_id: str
    ruleset_id: str
    mode: str
    alerts_generated: int
    attack_tp_count: int
    baseline_fp_count: int
    coverage_rate: Optional[float]
    verdict: str
    allowed_fp_threshold: int
    sample_alert_ids: list[str]
    sample_event_ids: list[str]
    started_at: str
    finished_at: str
