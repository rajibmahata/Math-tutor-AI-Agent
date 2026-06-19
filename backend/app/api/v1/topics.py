"""Topics & Curriculum API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.progress import ProgressService

router = APIRouter()


@router.get("")
async def get_topic_tree(
    grade: str = Query(default="1"),
    board: str = Query(default="ncert"),
    db: AsyncSession = Depends(get_db),
):
    """Get the full topic tree for a grade and board."""
    service = ProgressService(db)
    return await service.get_topic_tree(grade, board)


@router.get("/next/{student_id}")
async def get_next_topic(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the recommended next topic for a student."""
    from uuid import UUID
    from sqlalchemy import select, and_
    from app.models.student import Student
    from app.models.student_topic_progress import StudentTopicProgress
    from app.models.topic import Topic

    # Get student
    result = await db.execute(select(Student).where(Student.id == UUID(student_id)))
    student = result.scalar_one_or_none()
    if not student:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Student", student_id)

    # Get all topics for this grade not yet mastered
    mastered_ids_result = await db.execute(
        select(StudentTopicProgress.topic_id).where(
            and_(
                StudentTopicProgress.student_id == UUID(student_id),
                StudentTopicProgress.mastery_score >= 0.85,
            )
        )
    )
    mastered_ids = {r[0] for r in mastered_ids_result.all()}

    # Find next topics
    result = await db.execute(
        select(Topic)
        .where(
            and_(
                Topic.grade_start == student.grade,
                Topic.id.notin_(mastered_ids) if mastered_ids else True,
            )
        )
        .order_by(Topic.topic_order)
        .limit(1)
    )
    next_topic = result.scalar_one_or_none()

    return {
        "recommended_topic": {
            "id": str(next_topic.id) if next_topic else None,
            "name": next_topic.name_en if next_topic else "Keep practicing current topics",
            "reason": "Next topic in your grade curriculum" if next_topic else "Review previous topics",
        },
    }
