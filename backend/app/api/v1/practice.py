"""Practice API endpoints — quiz generation, submission, completion."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_student
from app.models.student import Student
from app.services.practice import PracticeService
from app.schemas.common import GeneratePracticeRequest, SubmitAnswerRequest

router = APIRouter()


@router.post("/generate")
async def generate_practice(
    body: GeneratePracticeRequest,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Generate an adaptive practice quiz."""
    service = PracticeService(db)
    try:
        practice_set = await service.generate_practice_set(
            student_id=student.id,
            topic_id=UUID(body.topic_id) if body.topic_id else None,
            difficulty=body.difficulty,
            question_count=body.question_count,
            language=body.language,
        )
        await db.commit()

        # Load questions
        from sqlalchemy import select
        from app.models.practice_question import PracticeQuestion

        q_result = await db.execute(
            select(PracticeQuestion)
            .where(PracticeQuestion.practice_set_id == practice_set.id)
            .order_by(PracticeQuestion.question_number)
        )
        questions = q_result.scalars().all()

        return {
            "id": str(practice_set.id),
            "title": practice_set.title,
            "topic": None,
            "difficulty": practice_set.difficulty,
            "question_count": practice_set.question_count,
            "questions": [
                {
                    "question_number": q.question_number,
                    "question_text": q.question_text,
                    "question_latex": q.question_latex,
                    "difficulty": q.difficulty,
                    "hints": q.hints or [],
                }
                for q in questions
            ],
            "status": practice_set.status,
        }
    except Exception:
        await db.rollback()
        raise


@router.post("/{practice_set_id}/questions/{question_number}/answer")
async def submit_answer(
    practice_set_id: str,
    question_number: int,
    body: SubmitAnswerRequest,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Submit an answer for a practice question."""
    service = PracticeService(db)
    try:
        result = await service.submit_answer(
            practice_set_id=UUID(practice_set_id),
            question_number=question_number,
            answer=body.answer,
            time_taken_seconds=body.time_taken_seconds,
            hints_used=body.hints_used,
        )
        await db.commit()
        result["new_streak"] = student.current_streak
        return result
    except Exception:
        await db.rollback()
        raise


@router.post("/{practice_set_id}/complete")
async def complete_practice(
    practice_set_id: str,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Complete a practice set and get results."""
    service = PracticeService(db)
    try:
        result = await service.complete_practice(UUID(practice_set_id))
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        raise


@router.get("/{practice_set_id}")
async def get_practice_set(
    practice_set_id: str,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get a practice set with all questions and answers."""
    from sqlalchemy import select
    from app.models.practice_set import PracticeSet
    from app.models.practice_question import PracticeQuestion

    result = await db.execute(
        select(PracticeSet).where(PracticeSet.id == UUID(practice_set_id))
    )
    practice_set = result.scalar_one_or_none()
    if not practice_set:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("PracticeSet", practice_set_id)

    q_result = await db.execute(
        select(PracticeQuestion)
        .where(PracticeQuestion.practice_set_id == UUID(practice_set_id))
        .order_by(PracticeQuestion.question_number)
    )
    questions = q_result.scalars().all()

    return {
        "id": str(practice_set.id),
        "title": practice_set.title,
        "difficulty": practice_set.difficulty,
        "question_count": practice_set.question_count,
        "score": practice_set.score,
        "max_score": practice_set.max_score,
        "status": practice_set.status,
        "questions": [
            {
                "question_number": q.question_number,
                "question_text": q.question_text,
                "correct_answer": q.correct_answer if practice_set.status == "completed" else None,
                "student_answer": q.student_answer,
                "is_correct": q.is_correct,
                "solution_steps": q.solution_steps if practice_set.status == "completed" else None,
            }
            for q in questions
        ],
    }
