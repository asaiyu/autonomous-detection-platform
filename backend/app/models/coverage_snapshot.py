from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CoverageSnapshot(Base):
    __tablename__ = "coverage_snapshots"

    id: Mapped[uuid.UUID] = mapped_column("snapshot_id", Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ruleset_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("rulesets.id"), nullable=True)
    dataset_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ruleset_id_text: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metrics_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    coverage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
