"""Content Pipeline API — PDF upload, AI generation, and tutor validation workflow."""

import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tutor import Tutor
from app.models.content import SourceDocument, ContentLesson
from app.services.content import content_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Admin: Upload source documents
# ---------------------------------------------------------------------------

@router.post("/documents", status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    subject: str = Form(default="Mathematics"),
    grade: str = Form(default="3"),
    language: str = Form(default="en"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Admin uploads a PDF/document. The system:
    1. Saves the file
    2. Queues text extraction
    3. Queues AI lesson generation
    4. Notifies all available tutors for review
    """
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    allowed_types = {"pdf", "txt", "md"}
    file_ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_ext}'. Allowed: {allowed_types}",
        )

    file_bytes = await file.read()
    if len(file_bytes) > 50 * 1024 * 1024:  # 50 MB guard
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    doc = await content_service.save_source_document(
        db,
        title=title,
        file_bytes=file_bytes,
        file_type=file_ext,
        uploaded_by=current_user.id,
        subject=subject,
        grade=grade,
        language=language,
    )

    # Run extraction + generation in background so the response is immediate
    async def _pipeline(document_id: uuid.UUID, uploader_id: uuid.UUID) -> None:
        from app.core.database import async_session
        async with async_session() as bg_db:
            await content_service.extract_text_from_document(bg_db, document_id)

            # Fetch active tutors to notify
            r = await bg_db.execute(
                select(Tutor.user_id).where(
                    Tutor.verification_status == "admin_approved",
                    Tutor.is_active.is_(True),
                )
            )
            tutor_user_ids = [row[0] for row in r.all()]

            await content_service.generate_lessons_from_document(
                bg_db,
                document_id,
                tutor_user_ids=tutor_user_ids,
                grade=grade,
                subject=subject,
            )

    background_tasks.add_task(_pipeline, doc.id, current_user.id)

    return {
        "id": str(doc.id),
        "title": doc.title,
        "file_type": doc.file_type,
        "subject": doc.subject,
        "grade": doc.grade,
        "language": doc.language,
        "extraction_status": doc.extraction_status,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "message": "Document uploaded. AI processing started in background.",
    }


@router.get("/documents")
async def list_documents(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all uploaded source documents (admin/principal)."""
    if current_user.role not in ("admin", "principal"):
        raise HTTPException(status_code=403, detail="Admin or principal role required")

    result = await db.execute(
        select(SourceDocument)
        .order_by(SourceDocument.uploaded_at.desc())
        .limit(limit)
    )
    docs = result.scalars().all()
    return {
        "data": [
            {
                "id": str(d.id),
                "title": d.title,
                "subject": d.subject,
                "grade": d.grade,
                "language": d.language,
                "file_type": d.file_type,
                "extraction_status": d.extraction_status,
                "uploaded_at": d.uploaded_at.isoformat(),
            }
            for d in docs
        ]
    }


# ---------------------------------------------------------------------------
# Tutor: Content review
# ---------------------------------------------------------------------------

@router.get("/lessons/pending")
async def list_pending_lessons(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tutors see AI-generated lessons that need their review."""
    if current_user.role not in ("tutor", "admin"):
        raise HTTPException(status_code=403, detail="Tutor role required")

    lessons = await content_service.list_pending_review(db)
    return {
        "data": [
            {
                "id": str(l.id),
                "title": l.title,
                "language": l.language,
                "status": l.status,
                "content_preview": (l.content_text or "")[:300] + "..." if l.content_text and len(l.content_text) > 300 else l.content_text,
                "created_at": l.created_at.isoformat(),
            }
            for l in lessons
        ]
    }


@router.get("/lessons/{lesson_id}")
async def get_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full lesson content for review or display."""
    lid = uuid.UUID(lesson_id)
    result = await db.execute(select(ContentLesson).where(ContentLesson.id == lid))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return {
        "id": str(lesson.id),
        "title": lesson.title,
        "language": lesson.language,
        "status": lesson.status,
        "content_text": lesson.content_text,
        "created_by": lesson.created_by,
        "created_at": lesson.created_at.isoformat(),
        "reviewed_at": lesson.reviewed_at.isoformat() if lesson.reviewed_at else None,
        "published_at": lesson.published_at.isoformat() if lesson.published_at else None,
    }


class ReviewRequest(BaseModel):
    action: str  # "approve" | "reject" | "modify"
    feedback: Optional[str] = None
    modified_content: Optional[str] = None
    accuracy_score: Optional[float] = None
    completeness_score: Optional[float] = None
    alignment_score: Optional[float] = None


@router.post("/lessons/{lesson_id}/review")
async def review_lesson(
    lesson_id: str,
    body: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tutor reviews an AI-generated lesson:
    - approve → published immediately
    - reject  → sent back; admin notified
    - modify  → tutor edits inline, then published
    """
    if current_user.role not in ("tutor", "admin"):
        raise HTTPException(status_code=403, detail="Tutor role required")

    # Resolve tutor record
    tutor_result = await db.execute(
        select(Tutor).where(Tutor.user_id == current_user.id)
    )
    tutor = tutor_result.scalar_one_or_none()
    if not tutor and current_user.role == "tutor":
        raise HTTPException(status_code=404, detail="Tutor profile not found")

    tutor_id = tutor.id if tutor else uuid.uuid4()  # admin fallback

    lid = uuid.UUID(lesson_id)
    lesson = await content_service.review_lesson(
        db,
        lesson_id=lid,
        tutor_id=tutor_id,
        tutor_user_id=current_user.id,
        action=body.action,
        feedback=body.feedback,
        modified_content=body.modified_content,
        accuracy_score=body.accuracy_score,
        completeness_score=body.completeness_score,
        alignment_score=body.alignment_score,
    )
    return {
        "id": str(lesson.id),
        "status": lesson.status,
        "action_taken": body.action,
        "reviewed_at": lesson.reviewed_at.isoformat() if lesson.reviewed_at else None,
        "published_at": lesson.published_at.isoformat() if lesson.published_at else None,
    }


# ---------------------------------------------------------------------------
# Public: Fetch published lessons
# ---------------------------------------------------------------------------

@router.get("/lessons")
async def list_published_lessons(
    language: Optional[str] = Query(default=None),
    grade: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Return published lessons (accessible to students)."""
    lessons = await content_service.list_published(db, language=language, grade=grade, limit=limit)
    return {
        "data": [
            {
                "id": str(l.id),
                "title": l.title,
                "language": l.language,
                "content_text": l.content_text,
                "published_at": l.published_at.isoformat() if l.published_at else None,
            }
            for l in lessons
        ]
    }
