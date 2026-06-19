"""TopicPrerequisite model — prerequisite relationships between topics."""

import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TopicPrerequisite(Base):
    __tablename__ = "topic_prerequisites"
    __table_args__ = (
        UniqueConstraint("topic_id", "prerequisite_id"),
        CheckConstraint("topic_id != prerequisite_id", name="ck_topic_not_self_prereq"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    prerequisite_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    importance: Mapped[str] = mapped_column(
        String(20), nullable=False, default="required"
    )

    topic = relationship("Topic", foreign_keys=[topic_id], back_populates="prerequisites")
    prerequisite = relationship("Topic", foreign_keys=[prerequisite_id], back_populates="required_by")
