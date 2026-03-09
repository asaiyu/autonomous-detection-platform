from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CoverageEvaluation(Base):
    __tablename__ = "coverage_evaluations"

    id: Mapped[uuid.UUID] = mapped_column("evaluation_id", Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("attack_runs.run_id"), nullable=False)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("attack_runs.run_id"), nullable=True)
    finding_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("findings.finding_id"), nullable=True)
    ruleset_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("rulesets.id"), nullable=True)
    scenario: Mapped[str] = mapped_column(String(128), nullable=False)
    result: Mapped[str] = mapped_column(String(64), nullable=False)
    coverage_state: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    window_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    window_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    related_event_ids_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    related_alert_ids_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    missing_telemetry_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
