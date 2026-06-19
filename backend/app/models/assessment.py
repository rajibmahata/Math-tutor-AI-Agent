"""Assessment model — per-question evaluation records."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True, index=True
    )

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_latex: Mapped[str] = mapped_column(Text, nullable=True)
    student_answer: Mapped[str] = mapped_column(Text, nullable=False)
    student_answer_latex: Mapped[str] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer_latex: Mapped[str] = mapped_column(Text, nullable=True)

    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    sympy_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    error_type: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    misconception: Mapped[str] = mapped_column(Text, nullable=True)
    prerequisite_topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True
    )

    difficulty_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    message = relationship("Message", back_populates="assessment")
    student = relationship("Student", back_populates="assessments")
    topic = relationship("Topic", foreign_keys=[topic_id])
    prerequisite_topic = relationship("Topic", foreign_keys=[prerequisite_topic_id])
