"""Student model — the Digital Twin."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    # Basic Profile
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    preferred_language: Mapped[str] = mapped_column(String(5), nullable=False, default="en", index=True)
    board: Mapped[str] = mapped_column(String(50), nullable=False, default="ncert")

    # Learning Profile (Digital Twin Core)
    learning_speed: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accuracy_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_time_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Current State
    current_topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True
    )
    last_session_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    placement_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="student")
    parent = relationship("User", foreign_keys=[parent_id])
    current_topic = relationship("Topic", foreign_keys=[current_topic_id])
    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")
    topic_progress = relationship("StudentTopicProgress", back_populates="student", cascade="all, delete-orphan")
    practice_sets = relationship("PracticeSet", back_populates="student", cascade="all, delete-orphan")
    achievements = relationship("StudentAchievement", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="student")
    reports = relationship("ParentReport", back_populates="student")
