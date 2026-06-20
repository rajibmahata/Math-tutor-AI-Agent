"""Tutor API endpoints — registration, verification, dashboard, feedback, content review."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tutor import Tutor, TutorDocument, Principal
from app.models.student import Student
from app.models.session import Session as TutoringSession
from app.models.student_topic_progress import StudentTopicProgress
from app.models.notification import NotificationType, NotificationPriority
from app.services.notification import notification_service

router = APIRouter()


class TutorRegisterRequest(BaseModel):
    subjects: list = []  # [{"subject":"Math","grade_start":"1","grade_end":"8"}]
    experience_yrs: int = 0
    bio: str = ""


@router.post("/register", status_code=201)
async def register_tutor(
    body: TutorRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register as a tutor."""
    if current_user.role not in ("tutor", "admin"):
        raise HTTPException(status_code=403, detail="Must have tutor or admin role")

    r = await db.execute(select(Tutor).where(Tutor.user_id == current_user.id))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tutor profile already exists")

    tutor = Tutor(
        id=uuid.uuid4(),
        user_id=current_user.id,
        subjects=body.subjects,
        experience_yrs=body.experience_yrs,
        bio=body.bio,
        verification_status="pending",
    )
    db.add(tutor)
    await db.commit()

    return {
        "id": str(tutor.id),
        "user_id": str(tutor.user_id),
        "subjects": tutor.subjects,
        "experience_yrs": tutor.experience_yrs,
        "verification_status": tutor.verification_status,
    }


@router.get("/dashboard")
async def my_tutor_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard for the currently logged-in tutor."""
    r = await db.execute(select(Tutor).where(Tutor.user_id == current_user.id))
    tutor = r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor profile not found. Register first.")
    return {
        "tutor_id": str(tutor.id), "assigned_students": tutor.total_students or 0,
        "rating": tutor.rating, "verification_status": tutor.verification_status,
        "subjects": tutor.subjects, "experience_yrs": tutor.experience_yrs,
    }


@router.get("/{tutor_id}")
async def get_tutor(tutor_id: str, db: AsyncSession = Depends(get_db)):
    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    tutor = r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {
        "id": str(tutor.id), "user_id": str(tutor.user_id),
        "subjects": tutor.subjects, "experience_yrs": tutor.experience_yrs,
        "bio": tutor.bio, "verification_status": tutor.verification_status,
        "rating": tutor.rating, "total_students": tutor.total_students,
        "is_active": tutor.is_active,
    }


@router.get("/{tutor_id}/dashboard")
async def tutor_dashboard_by_id(tutor_id: str, db: AsyncSession = Depends(get_db)):
    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    tutor = r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {
        "tutor_id": str(tutor.id), "assigned_students": tutor.total_students or 0,
        "rating": tutor.rating, "verification_status": tutor.verification_status,
    }


@router.post("/{tutor_id}/documents", status_code=201)
async def upload_tutor_document(
    tutor_id: str, file: UploadFile = File(...), doc_type: str = Form(...),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    import os
    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Tutor not found")
    upload_dir = "/tmp/vidyamitra/tutor_docs"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{tutor_id}_{doc_type}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    doc = TutorDocument(id=uuid.uuid4(), tutor_id=tid, doc_type=doc_type, file_url=file_path)
    db.add(doc)
    await db.commit()
    return {"id": str(doc.id), "doc_type": doc_type, "status": "uploaded"}


# ---------------------------------------------------------------------------
# Assigned students — view performance for tutor's students
# ---------------------------------------------------------------------------

@router.get("/students")
async def my_assigned_students(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all students assigned to the current tutor with performance summary."""
    if current_user.role not in ("tutor", "admin"):
        raise HTTPException(status_code=403, detail="Tutor role required")

    tutor_r = await db.execute(select(Tutor).where(Tutor.user_id == current_user.id))
    tutor = tutor_r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor profile not found")

    # Students whose tutor_id matches this tutor
    student_r = await db.execute(
        select(Student, User)
        .join(User, User.id == Student.user_id)
        .where(Student.tutor_id == tutor.id)
    )
    rows = student_r.all()

    data = []
    for student, user in rows:
        # Compute recent session count
        session_count_r = await db.execute(
            select(func.count(TutoringSession.id)).where(TutoringSession.student_id == student.id)
        )
        session_count = session_count_r.scalar() or 0

        # Weak topics
        weak_r = await db.execute(
            select(StudentTopicProgress)
            .where(
                StudentTopicProgress.student_id == student.id,
                StudentTopicProgress.is_weak.is_(True),
            )
            .limit(3)
        )
        weak_topics = [
            {"topic_id": str(p.topic_id), "accuracy": round(p.accuracy_rate, 2)}
            for p in weak_r.scalars().all()
        ]

        data.append({
            "student_id": str(student.id),
            "name": user.full_name,
            "email": user.email,
            "grade": student.grade,
            "preferred_language": student.preferred_language,
            "accuracy_rate": round(student.accuracy_rate, 2),
            "current_streak": student.current_streak,
            "total_points": student.total_points,
            "total_sessions": session_count,
            "weak_topics": weak_topics,
            "last_session_at": student.last_session_at.isoformat() if student.last_session_at else None,
        })

    return {"data": data, "total": len(data)}


# ---------------------------------------------------------------------------
# Feedback — tutor sends feedback to a student
# ---------------------------------------------------------------------------

class TutorFeedbackRequest(BaseModel):
    student_id: str
    message: str
    recommendations: list[str] = []
    study_plan: Optional[str] = None


@router.post("/feedback", status_code=201)
async def send_feedback_to_student(
    body: TutorFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tutor sends personalized feedback/recommendations to a student."""
    if current_user.role not in ("tutor", "admin"):
        raise HTTPException(status_code=403, detail="Tutor role required")

    student_id = uuid.UUID(body.student_id)
    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Notify student
    await notification_service.create(
        db,
        user_id=student.user_id,
        notification_type=NotificationType.TUTOR_FEEDBACK,
        title="Your tutor sent you feedback",
        body=body.message[:300],
        priority=NotificationPriority.HIGH,
        action_url="/dashboard?tab=feedback",
        entity_type="tutor_feedback",
    )

    return {
        "status": "sent",
        "student_id": body.student_id,
        "message": body.message,
        "recommendations": body.recommendations,
        "study_plan": body.study_plan,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Reassignment — tutor requests to be reassigned from a student
# ---------------------------------------------------------------------------

class ReassignmentRequest(BaseModel):
    student_id: str
    reason: str


@router.post("/reassignment-requests", status_code=201)
async def request_reassignment(
    body: ReassignmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tutor requests reassignment from a student.
    A reason must be provided; principal approval is required.
    """
    if current_user.role not in ("tutor",):
        raise HTTPException(status_code=403, detail="Tutor role required")

    if not body.reason.strip():
        raise HTTPException(status_code=400, detail="A reason is required for reassignment")

    student_id = uuid.UUID(body.student_id)
    student_r = await db.execute(select(Student).where(Student.id == student_id))
    student = student_r.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Notify all principals
    principal_r = await db.execute(
        select(Principal).where(Principal.is_active.is_(True))
    )
    principals = principal_r.scalars().all()
    for principal in principals:
        try:
            await notification_service.create(
                db,
                user_id=principal.user_id,
                notification_type=NotificationType.TUTOR_REASSIGNMENT_REQUEST,
                title="Tutor reassignment request",
                body=f"Tutor {current_user.full_name} requests reassignment from student. Reason: {body.reason}",
                priority=NotificationPriority.HIGH,
                action_url="/principal?tab=approvals",
                entity_type="reassignment_request",
            )
        except Exception:
            pass

    return {
        "status": "submitted",
        "student_id": body.student_id,
        "reason": body.reason,
        "message": "Reassignment request submitted. Awaiting principal approval.",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Notifications — tutor's pending action items
# ---------------------------------------------------------------------------

@router.get("/notifications")
async def tutor_notifications(
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return unread/all notifications for the current tutor."""
    notifications, unread_count = await notification_service.list_for_user(
        db, current_user.id, unread_only=unread_only, limit=30
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
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ],
        "unread_count": unread_count,
    }

