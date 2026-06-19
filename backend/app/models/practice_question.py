"""PracticeQuestion — individual questions within a practice set."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PracticeQuestion(Base):
    __tablename__ = "practice_questions"
    __table_args__ = (UniqueConstraint("practice_set_id", "question_number"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    practice_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practice_sets.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_latex: Mapped[str] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer_latex: Mapped[str] = mapped_column(Text, nullable=True)
    solution_steps: Mapped[dict] = mapped_column(JSONB, nullable=True)
    difficulty: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    hints: Mapped[dict] = mapped_column(JSONB, nullable=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True, index=True
    )

    student_answer: Mapped[str] = mapped_column(Text, nullable=True)
    student_answer_latex: Mapped[str] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=True)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    hints_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    practice_set = relationship("PracticeSet", back_populates="questions")
    topic = relationship("Topic")
