"""PracticeSet model — generated practice quizzes."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PracticeSet(Base):
    __tablename__ = "practice_sets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True
    )
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False, default="adaptive"
    )
    question_count: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    student = relationship("Student", back_populates="practice_sets")
    topic = relationship("Topic")
    questions = relationship("PracticeQuestion", back_populates="practice_set", cascade="all, delete-orphan")
