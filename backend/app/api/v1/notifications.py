"""Notifications API — retrieve and manage user notifications."""

import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.notification import notification_service

router = APIRouter()


@router.get("")
async def list_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    notifications, unread_count = await notification_service.list_for_user(
        db,
        current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return {
        "data": [
            {
                "id": str(n.id),
                "type": n.notification_type,
                "priority": n.priority,
                "title": n.title,
                "body": n.body,
                "action_url": n.action_url,
                "entity_id": str(n.entity_id) if n.entity_id else None,
                "entity_type": n.entity_type,
                "is_read": n.is_read,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ],
        "unread_count": unread_count,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": len(notifications) == limit,
        },
    }


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a single notification as read."""
    nid = uuid.UUID(notification_id)
    updated = await notification_service.mark_read(db, nid, current_user.id)
    return {"success": updated}


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all unread notifications as read."""
    count = await notification_service.mark_all_read(db, current_user.id)
    return {"updated": count}
