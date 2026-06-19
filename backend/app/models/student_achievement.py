"""StudentAchievement — gamification and milestone tracking."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudentAchievement(Base):
    __tablename__ = "student_achievements"
    __table_args__ = (UniqueConstraint("student_id", "achievement_type"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    achievement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    title_hi: Mapped[str] = mapped_column(String(255), nullable=True)
    title_bn: Mapped[str] = mapped_column(String(255), nullable=True)
    description_en: Mapped[str] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str] = mapped_column(String(500), nullable=True)
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    student = relationship("Student", back_populates="achievements")
