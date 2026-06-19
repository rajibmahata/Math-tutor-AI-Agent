"""StudentTopicProgress — per-student, per-topic mastery tracking."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudentTopicProgress(Base):
    __tablename__ = "student_topic_progress"
    __table_args__ = (UniqueConstraint("student_id", "topic_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    questions_attempted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    questions_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accuracy_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    mastered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    times_reviewed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_weak: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    common_error_type: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    student = relationship("Student", back_populates="topic_progress")
    topic = relationship("Topic")
