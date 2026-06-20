"""Notification service — create and manage platform notifications."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.models.notification import Notification, NotificationType, NotificationPriority


class NotificationService:
    """CRUD and query operations for user notifications."""

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        action_url: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
    ) -> Notification:
        """Persist a new notification for a user."""
        notification = Notification(
            id=uuid.uuid4(),
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            priority=priority,
            action_url=action_url,
            entity_id=entity_id,
            entity_type=entity_type,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def list_for_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        *,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Notification], int]:
        """Return paginated notifications for a user plus total unread count."""
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read.is_(False))
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        notifications = list(result.scalars().all())

        # Unread count (always)
        unread_r = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        unread_count = unread_r.scalar() or 0

        return notifications, unread_count

    @staticmethod
    async def mark_read(
        db: AsyncSession, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Mark a single notification as read (verifies ownership)."""
        result = await db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await db.commit()
        return (result.rowcount or 0) > 0

    @staticmethod
    async def mark_all_read(db: AsyncSession, user_id: uuid.UUID) -> int:
        """Mark all unread notifications for a user as read. Returns rows updated."""
        result = await db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await db.commit()
        return result.rowcount or 0


notification_service = NotificationService()
