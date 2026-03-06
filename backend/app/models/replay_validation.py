from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReplayValidation(Base):
    __tablename__ = "replay_validations"

    id: Mapped[uuid.UUID] = mapped_column("validation_id", Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("attack_runs.run_id"), nullable=True)
    proposal_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("rule_proposals.proposal_id"), nullable=True)
    attack_dataset_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    baseline_dataset_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    replay_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    replay_finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    results_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    verdict: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
