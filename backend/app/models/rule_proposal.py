from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RuleProposal(Base):
    __tablename__ = "rule_proposals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("events.id"), nullable=True)
    evaluation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("coverage_evaluations.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    rule_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    rule_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    proposal_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    rule_yaml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    references_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    risk_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
