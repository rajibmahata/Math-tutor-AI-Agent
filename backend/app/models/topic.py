"""Topic model — curriculum topics with hierarchical structure."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True, index=True
    )

    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(255), nullable=True)
    name_bn: Mapped[str] = mapped_column(String(255), nullable=True)
    description_en: Mapped[str] = mapped_column(Text, nullable=True)
    description_hi: Mapped[str] = mapped_column(Text, nullable=True)
    description_bn: Mapped[str] = mapped_column(Text, nullable=True)

    grade_start: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    grade_end: Mapped[str] = mapped_column(String(5), nullable=True)
    board: Mapped[str] = mapped_column(String(50), nullable=False, default="ncert")
    topic_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    difficulty_base: Mapped[float] = mapped_column(Float, nullable=False, default=0.3)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    parent = relationship("Topic", remote_side=[id], backref="children")
    prerequisites = relationship(
        "TopicPrerequisite",
        foreign_keys="TopicPrerequisite.topic_id",
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    required_by = relationship(
        "TopicPrerequisite",
        foreign_keys="TopicPrerequisite.prerequisite_id",
        back_populates="prerequisite",
        cascade="all, delete-orphan",
    )
