"""Notification model — platform-wide notification system for all roles."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    # Tutor notifications
    CONTENT_PENDING_REVIEW = "content_pending_review"
    STUDENT_ASSIGNED = "student_assigned"
    SUBJECTIVE_ANSWER_PENDING = "subjective_answer_pending"
    REASSIGNMENT_REQUEST = "reassignment_request"
    REASSIGNMENT_APPROVED = "reassignment_approved"
    REASSIGNMENT_REJECTED = "reassignment_rejected"

    # Principal notifications
    TUTOR_APPROVAL_REQUEST = "tutor_approval_request"
    TUTOR_REASSIGNMENT_REQUEST = "tutor_reassignment_request"
    ESCALATION_RAISED = "escalation_raised"
    STUDENT_FEEDBACK_ALERT = "student_feedback_alert"
    CONTENT_FLAG = "content_flag"

    # Admin notifications
    FINAL_TUTOR_APPROVAL = "final_tutor_approval"
    PRINCIPAL_ESCALATION = "principal_escalation"
    PLATFORM_ALERT = "platform_alert"
    COMPLIANCE_EXCEPTION = "compliance_exception"

    # Student notifications
    CONTENT_PUBLISHED = "content_published"
    TUTOR_FEEDBACK = "tutor_feedback"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    REPORT_READY = "report_ready"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Platform notification for any user role."""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Recipient
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Classification
    notification_type = Column(
        Enum(NotificationType, name="notification_type_enum"),
        nullable=False,
    )
    priority = Column(
        Enum(NotificationPriority, name="notification_priority_enum"),
        default=NotificationPriority.MEDIUM,
    )

    # Content
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)

    # Deep link — front-end route to navigate to on click
    action_url = Column(String(512), nullable=True)

    # Reference to the related entity (polymorphic by type)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    entity_type = Column(String(64), nullable=True)  # e.g. "content_lesson", "tutor", "student"

    # State
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
