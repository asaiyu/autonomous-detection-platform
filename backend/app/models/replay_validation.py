import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReplayValidation(Base):
    __tablename__ = "replay_validations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("attack_runs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
