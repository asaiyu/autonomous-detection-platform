from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

ReplayMode = Literal["attack_validation", "baseline_validation", "full_evaluation"]


class ReplayRequest(BaseModel):
    dataset_id: str
    ruleset_id: str
    mode: ReplayMode


class ReplayResponse(BaseModel):
    dataset_id: str
    ruleset_id: str
    mode: ReplayMode
    alerts_generated: int
    attack_tp_count: int
    baseline_fp_count: int
    coverage_rate: Optional[float]
    verdict: Literal["PASS", "FAIL"]
    allowed_fp_threshold: int
    sample_alert_ids: list[str]
    sample_event_ids: list[str]
    started_at: str
    finished_at: str
