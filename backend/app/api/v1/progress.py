"""Progress & Analytics API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_student
from app.models.student import Student
from app.services.progress import ProgressService

router = APIRouter()


@router.get("/{student_id}")
async def get_progress(
    student_id: str,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive progress for a student."""
    # Verify student owns this data
    if str(student.id) != student_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("You can only view your own progress")

    service = ProgressService(db)
    return await service.get_progress(UUID(student_id))


@router.get("/{student_id}/topics/{topic_id}")
async def get_topic_progress(
    student_id: str,
    topic_id: str,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed progress for a specific topic."""
    if str(student.id) != student_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError()

    service = ProgressService(db)
    return await service.get_topic_progress(UUID(student_id), UUID(topic_id))
