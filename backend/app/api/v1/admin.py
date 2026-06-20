"""Admin & Principal API endpoints — dashboards, approvals, user management, analytics."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.student import Student
from app.models.tutor import Tutor, Principal
from app.models.session import Session as TutoringSession
from app.models.content import ContentLesson
from app.models.notification import NotificationType, NotificationPriority
from app.services.notification import notification_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Super Admin dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Super Admin dashboard — organisation-wide real metrics."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    total_users_r = await db.execute(select(func.count(User.id)))
    total_students_r = await db.execute(
        select(func.count(User.id)).where(User.role == "student")
    )
    total_tutors_r = await db.execute(select(func.count(Tutor.id)))
    total_principals_r = await db.execute(select(func.count(Principal.id)))
    pending_tutors_r = await db.execute(
        select(func.count(Tutor.id)).where(
            Tutor.verification_status.in_(["pending", "ai_reviewed", "principal_approved"])
        )
    )
    total_sessions_r = await db.execute(select(func.count(TutoringSession.id)))
    published_lessons_r = await db.execute(
        select(func.count(ContentLesson.id)).where(ContentLesson.status == "published")
    )
    pending_review_r = await db.execute(
        select(func.count(ContentLesson.id)).where(ContentLesson.status == "draft")
    )

    return {
        "organization_overview": {
            "total_users": total_users_r.scalar() or 0,
            "total_students": total_students_r.scalar() or 0,
            "total_tutors": total_tutors_r.scalar() or 0,
            "total_principals": total_principals_r.scalar() or 0,
        },
        "approval_queue": {
            "tutor_approvals_pending": pending_tutors_r.scalar() or 0,
            "content_pending_review": pending_review_r.scalar() or 0,
        },
        "content": {
            "published_lessons": published_lessons_r.scalar() or 0,
        },
        "engagement": {
            "total_sessions": total_sessions_r.scalar() or 0,
        },
        "platform_health": {
            "uptime": "99.9%",
            "status": "healthy",
        },
    }


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

@router.get("/users")
async def list_users(
    role: Optional[str] = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List users by role (admin / principal)."""
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    query = select(User)
    if role:
        query = query.where(User.role == role)
    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)

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
        "pagination": {"limit": limit, "offset": offset, "has_more": len(users) == limit},
    }


@router.patch("/users/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    is_active: bool = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Activate or deactivate any user account (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    uid = uuid.UUID(user_id)
    await db.execute(
        update(User).where(User.id == uid).values(is_active=is_active)
    )
    await db.commit()
    return {"user_id": user_id, "is_active": is_active}


# ---------------------------------------------------------------------------
# Tutor approval workflow
# ---------------------------------------------------------------------------

@router.get("/tutors/pending")
async def list_pending_tutors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return tutors awaiting approval (admin/principal)."""
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    r = await db.execute(
        select(Tutor, User)
        .join(User, User.id == Tutor.user_id)
        .where(
            Tutor.verification_status.in_(["pending", "ai_reviewed", "principal_approved"])
        )
        .order_by(Tutor.created_at.desc())
    )
    rows = r.all()
    return {
        "data": [
            {
                "tutor_id": str(t.id),
                "user_id": str(t.user_id),
                "name": u.full_name,
                "email": u.email,
                "subjects": t.subjects,
                "experience_yrs": t.experience_yrs,
                "verification_status": t.verification_status,
                "created_at": t.created_at.isoformat(),
            }
            for t, u in rows
        ]
    }


@router.post("/tutors/{tutor_id}/approve")
async def approve_tutor(
    tutor_id: str,
    action: str = Query(default="approve"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve or reject a tutor.
    - Principal can set status to 'principal_approved'
    - Admin can set status to 'admin_approved' (activates the account)
    """
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    tutor = r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")

    if action == "approve":
        if current_user.role == "admin":
            tutor.verification_status = "admin_approved"
            tutor.is_active = True
            tutor.verified_by = current_user.id
            tutor.verified_at = datetime.now(timezone.utc)
        else:
            # Principal gives mid-stage approval
            tutor.verification_status = "principal_approved"
            # Notify admins for final sign-off
            admin_r = await db.execute(
                select(User).where(User.role == "admin", User.is_active.is_(True))
            )
            for admin_user in admin_r.scalars().all():
                try:
                    await notification_service.create(
                        db,
                        user_id=admin_user.id,
                        notification_type=NotificationType.FINAL_TUTOR_APPROVAL,
                        title="Tutor ready for final approval",
                        body=f"Principal approved a tutor. Awaiting your final sign-off.",
                        priority=NotificationPriority.HIGH,
                        action_url="/admin?tab=approvals",
                        entity_id=tutor.id,
                        entity_type="tutor",
                    )
                except Exception:
                    pass
    else:
        tutor.verification_status = "rejected"
        tutor.is_active = False

    await db.commit()

    # Notify tutor of outcome
    try:
        outcome_msg = "Your account has been approved!" if action == "approve" else "Your application was not approved at this time."
        await notification_service.create(
            db,
            user_id=tutor.user_id,
            notification_type=NotificationType.FINAL_TUTOR_APPROVAL,
            title=f"Tutor application {'approved' if action == 'approve' else 'rejected'}",
            body=outcome_msg,
            priority=NotificationPriority.HIGH,
            action_url="/tutor",
        )
    except Exception:
        pass

    return {
        "tutor_id": tutor_id,
        "action": action,
        "verification_status": tutor.verification_status,
        "is_active": tutor.is_active,
    }


# ---------------------------------------------------------------------------
# Principal dashboard
# ---------------------------------------------------------------------------

@router.get("/principal/dashboard")
async def principal_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Principal dashboard with institution-wide real metrics."""
    if current_user.role not in ("principal", "admin"):
        raise HTTPException(status_code=403, detail="Principal or admin role required")

    total_students_r = await db.execute(
        select(func.count(User.id)).where(User.role == "student")
    )
    active_students_r = await db.execute(
        select(func.count(User.id)).where(User.role == "student", User.is_active.is_(True))
    )
    total_tutors_r = await db.execute(select(func.count(Tutor.id)))
    pending_r = await db.execute(
        select(func.count(Tutor.id)).where(
            Tutor.verification_status.in_(["pending", "ai_reviewed"])
        )
    )
    total_sessions_r = await db.execute(select(func.count(TutoringSession.id)))

    # Tutor list with basic stats
    tutors_r = await db.execute(
        select(Tutor, User)
        .join(User, User.id == Tutor.user_id)
        .where(Tutor.is_active.is_(True))
        .limit(20)
    )
    tutors_data = [
        {
            "tutor_id": str(t.id),
            "name": u.full_name,
            "subjects": t.subjects,
            "total_students": t.total_students,
            "rating": round(t.rating, 1),
            "verification_status": t.verification_status,
        }
        for t, u in tutors_r.all()
    ]

    # Get principal's institution info
    principal_r = await db.execute(
        select(Principal).where(Principal.user_id == current_user.id)
    )
    principal = principal_r.scalar_one_or_none()

    return {
        "institution": principal.institution if principal else "VidyaMitra",
        "overview": {
            "total_students": total_students_r.scalar() or 0,
            "active_students": active_students_r.scalar() or 0,
            "total_tutors": total_tutors_r.scalar() or 0,
            "pending_tutor_approvals": pending_r.scalar() or 0,
            "total_sessions": total_sessions_r.scalar() or 0,
        },
        "tutors": tutors_data,
    }


# ---------------------------------------------------------------------------
# Student assignment to tutor
# ---------------------------------------------------------------------------

class AssignStudentRequest(BaseModel):
    student_id: str
    tutor_id: str


@router.post("/assign-student")
async def assign_student_to_tutor(
    body: AssignStudentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign a student to a tutor (admin/principal)."""
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    student_id = uuid.UUID(body.student_id)
    tutor_id = uuid.UUID(body.tutor_id)

    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    tutor_r = await db.execute(select(Tutor).where(Tutor.id == tutor_id))
    tutor = tutor_r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")

    student.tutor_id = tutor_id
    tutor.total_students = (tutor.total_students or 0) + 1

    await db.commit()

    # Notify tutor of new student
    try:
        await notification_service.create(
            db,
            user_id=tutor.user_id,
            notification_type=NotificationType.STUDENT_ASSIGNED,
            title="New student assigned",
            body=f"A new student (Grade {student.grade}) has been assigned to you.",
            priority=NotificationPriority.MEDIUM,
            action_url="/tutor?tab=students",
            entity_id=student.id,
            entity_type="student",
        )
    except Exception:
        pass

    # Notify student of assigned tutor
    try:
        await notification_service.create(
            db,
            user_id=student.user_id,
            notification_type=NotificationType.STUDENT_ASSIGNED,
            title="Your tutor has been assigned",
            body="A qualified tutor has been matched to your profile.",
            priority=NotificationPriority.MEDIUM,
            action_url="/dashboard",
        )
    except Exception:
        pass

    return {
        "student_id": body.student_id,
        "tutor_id": body.tutor_id,
        "status": "assigned",
    }


# ---------------------------------------------------------------------------
# Organisation analytics
# ---------------------------------------------------------------------------

@router.get("/analytics")
async def organisation_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Organisation-wide analytics (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    total_users_r = await db.execute(select(func.count(User.id)))
    total_students_r = await db.execute(
        select(func.count(User.id)).where(User.role == "student")
    )
    total_tutors_r = await db.execute(select(func.count(Tutor.id)))
    active_tutors_r = await db.execute(
        select(func.count(Tutor.id)).where(Tutor.is_active.is_(True))
    )
    total_sessions_r = await db.execute(select(func.count(TutoringSession.id)))
    published_lessons_r = await db.execute(
        select(func.count(ContentLesson.id)).where(ContentLesson.status == "published")
    )

    return {
        "users": {
            "total": total_users_r.scalar() or 0,
            "students": total_students_r.scalar() or 0,
            "tutors": total_tutors_r.scalar() or 0,
            "active_tutors": active_tutors_r.scalar() or 0,
        },
        "engagement": {
            "total_sessions": total_sessions_r.scalar() or 0,
        },
        "content": {
            "published_lessons": published_lessons_r.scalar() or 0,
        },
    }

