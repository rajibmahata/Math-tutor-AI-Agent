"""KnowledgeDocument — metadata for RAG documents stored in Qdrant."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True, index=True
    )
    grade: Mapped[str] = mapped_column(String(5), nullable=True, index=True)
    language: Mapped[str] = mapped_column(String(5), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qdrant_collection: Mapped[str] = mapped_column(
        String(100), nullable=False, default="curriculum"
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    file_hash: Mapped[str] = mapped_column(String(64), nullable=True)

    topic = relationship("Topic")
