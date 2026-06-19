"""ParentReport — auto-generated progress reports for parents."""

import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON as JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ParentReport(Base):
    __tablename__ = "parent_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    report_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="weekly"
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    report_data: Mapped[dict] = mapped_column(JSON().with_variant(JSON, "postgresql"), nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=True)
    key_strengths: Mapped[dict] = mapped_column(JSON().with_variant(JSON, "postgresql"), nullable=True)
    key_weaknesses: Mapped[dict] = mapped_column(JSON().with_variant(JSON, "postgresql"), nullable=True)
    recommendations: Mapped[dict] = mapped_column(JSON().with_variant(JSON, "postgresql"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    student = relationship("Student")
    parent = relationship("User", foreign_keys=[parent_id])
