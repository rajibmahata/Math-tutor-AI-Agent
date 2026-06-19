"""Message model — individual messages within a tutoring session."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="text", index=True
    )
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="en")
    hint_level: Mapped[int] = mapped_column(Integer, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=True)
    math_expression: Mapped[str] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=True)
    model_used: Mapped[str] = mapped_column(String(50), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("Session", back_populates="messages")
    assessment = relationship("Assessment", back_populates="message", uselist=False, cascade="all, delete-orphan")
