"""Curriculum, Content, and Approval models for v2.0."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CurriculumNode(Base):
    __tablename__ = "curriculum_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_nodes.id"), nullable=True, index=True
    )
    node_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_hi: Mapped[str] = mapped_column(String(255), nullable=True)
    name_bn: Mapped[str] = mapped_column(String(255), nullable=True)
    name_ta: Mapped[str] = mapped_column(String(255), nullable=True)
    grade_start: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    grade_end: Mapped[str] = mapped_column(String(5), nullable=True)
    board: Mapped[str] = mapped_column(String(50), default="ncert")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), default="pdf")
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(100), nullable=True)
    grade: Mapped[str] = mapped_column(String(5), nullable=True)
    language: Mapped[str] = mapped_column(String(5), nullable=True)
    extraction_status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending|processing|completed|failed
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding_model: Mapped[str] = mapped_column(String(50), default="text-embedding-3-small")
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ContentLesson(Base):
    __tablename__ = "content_lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    curriculum_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_nodes.id"), nullable=True, index=True
    )
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_documents.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=True)
    content_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="en", index=True)
    region: Mapped[str] = mapped_column(String(50), nullable=True)
    culture_context: Mapped[str] = mapped_column(String(50), nullable=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=True)
    audio_url: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True
    )  # draft|review|published|rejected
    created_by: Mapped[str] = mapped_column(String(20), default="ai")
    reviewed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tutors.id"), nullable=True
    )
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ContentReview(Base):
    __tablename__ = "content_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_lessons.id", ondelete="CASCADE"),
        nullable=False
    )
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tutors.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=True)
    accuracy_score: Mapped[float] = mapped_column(Float, nullable=True)
    completeness_score: Mapped[float] = mapped_column(Float, nullable=True)
    alignment_score: Mapped[float] = mapped_column(Float, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workflow_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    current_step: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    steps_history: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
