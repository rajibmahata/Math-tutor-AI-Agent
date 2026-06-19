"""Achievements API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_student
from app.models.student import Student
from app.models.student_achievement import StudentAchievement

router = APIRouter()


@router.get("/{student_id}")
async def get_achievements(
    student_id: str,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get all achievements for a student."""
    if str(student.id) != student_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("You can only view your own achievements")

    result = await db.execute(
        select(StudentAchievement)
        .where(StudentAchievement.student_id == UUID(student_id))
        .order_by(StudentAchievement.earned_at.desc())
    )
    achievements = result.scalars().all()

    earned = [
        {
            "type": a.achievement_type,
            "title": a.title_en,
            "description": a.description_en or "",
            "earned_at": a.earned_at.isoformat() if a.earned_at else None,
        }
        for a in achievements
    ]

    # Define all possible achievements and check progress toward unearned ones
    all_achievement_types = {
        "streak_3": ("3-Day Streak! 🔥", "Learn for 3 days in a row"),
        "streak_7": ("7-Day Streak! 🔥🔥", "Learn for 7 days in a row"),
        "questions_100": ("Century! 💯", "Answer 100 questions"),
        "questions_500": ("500 Club! 🏆", "Answer 500 questions"),
        "accuracy_80": ("Sharpshooter! 🎯", "Reach 80% accuracy"),
        "accuracy_90": ("Math Wizard! 🧙", "Reach 90% accuracy"),
    }

    earned_types = {a["type"] for a in earned}
    next_achievements = []
    for ach_type, (title, desc) in all_achievement_types.items():
        if ach_type not in earned_types:
            # Calculate progress
            if ach_type == "streak_3":
                progress = {"current": min(student.current_streak, 3), "target": 3}
            elif ach_type == "streak_7":
                progress = {"current": min(student.current_streak, 7), "target": 7}
            elif ach_type == "questions_100":
                progress = {"current": min(student.total_questions, 100), "target": 100}
            elif ach_type == "questions_500":
                progress = {"current": min(student.total_questions, 500), "target": 500}
            elif ach_type == "accuracy_80":
                progress = {"current": round(min(student.accuracy_rate, 0.8) * 100), "target": 80}
            elif ach_type == "accuracy_90":
                progress = {"current": round(min(student.accuracy_rate, 0.9) * 100), "target": 90}
            else:
                progress = {"current": 0, "target": 1}

            next_achievements.append({
                "type": ach_type,
                "title": title,
                "progress": progress,
            })

    return {
        "achievements": earned,
        "next_achievements": next_achievements[:5],
    }
