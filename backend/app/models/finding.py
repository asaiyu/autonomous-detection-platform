from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column("finding_id", Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("attack_runs.run_id"), nullable=False)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("attack_runs.run_id"), nullable=True)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("events.event_id"), nullable=True)
    alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("alerts.alert_id"), nullable=True)
    finding_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    entrypoint_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    proof_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tags_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    detail: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
