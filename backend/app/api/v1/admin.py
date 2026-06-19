"""Admin & Principal API endpoints — dashboards, approvals, user management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tutor import Tutor, Principal

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Super Admin dashboard — organization-wide overview."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    # Count users by role
    total_users_r = await db.execute(select(func.count(User.id)))
    total_users = total_users_r.scalar() or 0

    tutors_r = await db.execute(select(func.count(Tutor.id)))
    total_tutors = tutors_r.scalar() or 0

    pending_tutors_r = await db.execute(
        select(func.count(Tutor.id)).where(Tutor.verification_status == "pending")
    )
    pending_tutors = pending_tutors_r.scalar() or 0

    return {
        "organization_overview": {
            "total_users": total_users,
            "total_tutors": total_tutors,
            "approvals_pending": {
                "tutor_approvals": pending_tutors,
            },
        },
        "platform_health": {
            "uptime": "99.9%",
            "status": "healthy",
        },
    }


@router.get("/users")
async def list_users(
    role: str = Query(default=None),
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List users by role (admin only)."""
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    query = select(User)
    if role:
        query = query.where(User.role == role)
    query = query.order_by(User.created_at.desc()).limit(limit)

    r = await db.execute(query)
    users = r.scalars().all()

    return {
        "data": [
            {
                "id": str(u.id),
                "full_name": u.full_name,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "pagination": {"has_more": len(users) == limit},
    }


@router.post("/tutors/{tutor_id}/approve")
async def approve_tutor(
    tutor_id: str,
    action: str = Query(default="approve"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a tutor (admin/principal)."""
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    import uuid
    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    tutor = r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")

    if action == "approve":
        tutor.verification_status = "admin_approved"
        tutor.is_active = True
    else:
        tutor.verification_status = "rejected"
        tutor.is_active = False

    await db.commit()
    return {"status": action + "d", "tutor_activated": tutor.is_active}


@router.get("/principal/dashboard")
async def principal_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Principal dashboard."""
    if current_user.role not in ("principal", "admin"):
        raise HTTPException(status_code=403, detail="Principal or admin role required")

    tutors_r = await db.execute(select(func.count(Tutor.id)))
    total_tutors = tutors_r.scalar() or 0

    pending_r = await db.execute(
        select(func.count(Tutor.id)).where(Tutor.verification_status.in_(["pending", "ai_reviewed"]))
    )
    pending = pending_r.scalar() or 0

    return {
        "institution": "VidyaMitra",
        "tutor_data": {
            "total": total_tutors,
            "pending_approvals": pending,
        },
        "escalations": [],
    }
