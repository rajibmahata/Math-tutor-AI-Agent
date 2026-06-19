"""Student Service — profile management, digital twin, placement assessment."""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.student import Student
from app.models.topic import Topic
from app.models.student_topic_progress import StudentTopicProgress

logger = logging.getLogger(__name__)


class StudentService:
    """Student profile and digital twin management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_profile(
        self,
        user_id: uuid.UUID,
        age: int,
        grade: str,
        preferred_language: str = "en",
        board: str = "ncert",
    ) -> Student:
        """Create a new student profile after signup."""
        # Check for existing profile
        result = await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        if result.scalar_one_or_none():
            from app.core.exceptions import DuplicateError
            raise DuplicateError("Student profile", "user_id")

        student = Student(
            id=uuid.uuid4(),
            user_id=user_id,
            age=age,
            grade=grade,
            preferred_language=preferred_language,
            board=board,
            learning_speed=5.0,
            confidence_score=0.5,
        )
        self.db.add(student)
        await self.db.flush()

        logger.info(f"Student profile created: {student.id} (grade {grade})")
        return student

    async def get_profile(self, student_id: uuid.UUID) -> Optional[Student]:
        """Get full student digital twin with relationships."""
        result = await self.db.execute(
            select(Student)
            .where(Student.id == student_id)
            .options(
                selectinload(Student.user),
                selectinload(Student.topic_progress).selectinload(StudentTopicProgress.topic),
                selectinload(Student.achievements),
            )
        )
        return result.scalar_one_or_none()

    async def get_profile_by_user(self, user_id: uuid.UUID) -> Optional[Student]:
        """Get student profile by user ID."""
        result = await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(
        self,
        student_id: uuid.UUID,
        **kwargs,
    ) -> Student:
        """Update student profile fields."""
        student = await self.get_profile(student_id)
        if not student:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Student", str(student_id))

        allowed_fields = {
            "age", "grade", "preferred_language", "board"
        }
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(student, key, value)

        student.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return student

    async def link_parent(
        self,
        student_id: uuid.UUID,
        parent_email: str,
        relationship: str = "parent",
    ) -> Student:
        """Link a parent user to this student."""
        student = await self.get_profile(student_id)
        if not student:
            raise NotFoundError("Student", str(student_id))

        # Find parent user
        result = await self.db.execute(
            select(User).where(
                and_(User.email == parent_email, User.role == "parent")
            )
        )
        parent = result.scalar_one_or_none()

        if not parent:
            from app.core.exceptions import AppException
            raise AppException(
                f"No parent account found with email: {parent_email}",
                status_code=404,
                error_type="parent_not_found",
            )

        if student.parent_id == parent.id:
            from app.core.exceptions import AppException
            raise AppException(
                "Parent already linked to this student",
                status_code=409,
                error_type="already_linked",
            )

        student.parent_id = parent.id
        await self.db.flush()
        logger.info(f"Parent {parent.id} linked to student {student_id}")
        return student

    async def get_digital_twin(self, student_id: uuid.UUID) -> dict:
        """Get the complete digital twin snapshot."""
        student = await self.get_profile(student_id)
        if not student:
            raise NotFoundError("Student", str(student_id))

        # Compute strengths and weaknesses from topic progress
        strengths = []
        weaknesses = []
        mastered_count = 0
        in_progress_count = 0

        for progress in student.topic_progress:
            topic = progress.topic
            if not topic:
                continue
            summary = {
                "topic_id": str(topic.id),
                "name": topic.name_en,
                "mastery_score": progress.mastery_score,
                "questions_attempted": progress.questions_attempted,
                "accuracy_rate": progress.accuracy_rate,
            }
            if progress.mastery_score >= 0.85:
                mastered_count += 1
                strengths.append(summary)
            elif progress.mastery_score > 0:
                in_progress_count += 1

            if progress.is_weak:
                weaknesses.append(summary)

        # Sort
        strengths.sort(key=lambda x: x["mastery_score"], reverse=True)
        weaknesses.sort(key=lambda x: x["mastery_score"])

        # Count total topics for this grade
        result = await self.db.execute(
            select(func.count(Topic.id)).where(Topic.grade_start <= student.grade)
        )
        total_topics = result.scalar() or 0

        remaining = max(0, total_topics - mastered_count - in_progress_count)

        progress_pct = round(mastered_count / max(total_topics, 1), 2)

        return {
            "id": student.id,
            "user_id": student.user_id,
            "age": student.age,
            "grade": student.grade,
            "preferred_language": student.preferred_language,
            "board": student.board,
            "learning_speed": student.learning_speed,
            "confidence_score": student.confidence_score,
            "accuracy_rate": student.accuracy_rate,
            "current_streak": student.current_streak,
            "longest_streak": student.longest_streak,
            "total_points": student.total_points,
            "total_sessions": student.total_sessions,
            "total_time_spent": student.total_time_spent,
            "total_questions": student.total_questions,
            "correct_answers": student.correct_answers,
            "current_topic": None,  # Will be populated with topic data
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "progress_summary": {
                "topics_mastered": mastered_count,
                "topics_in_progress": in_progress_count,
                "topics_remaining": remaining,
                "grade_progress_pct": progress_pct,
            },
            "placement_complete": student.placement_complete,
            "last_session_at": student.last_session_at.isoformat() if student.last_session_at else None,
        }

    async def generate_placement_questions(self, student_id: uuid.UUID) -> list[dict]:
        """Generate placement assessment questions for new students."""
        student = await self.get_profile(student_id)
        if not student:
            raise NotFoundError("Student", str(student_id))

        # Get grade-appropriate topics
        result = await self.db.execute(
            select(Topic)
            .where(Topic.grade_start == student.grade)
            .order_by(Topic.topic_order)
            .limit(5)
        )
        topics = result.scalars().all()

        # Generate 5 placement questions at increasing difficulty
        # In production, this would use the Practice Agent (LLM)
        # For MVP, we use template questions
        placement_questions = []
        for i, topic in enumerate(topics[:5]):
            difficulty = 0.2 + (i * 0.15)  # 0.2 to 0.8
            q = self._generate_placement_question(topic, i + 1, difficulty)
            placement_questions.append(q)

        # If not enough topics, add generic questions
        while len(placement_questions) < 5:
            i = len(placement_questions)
            placement_questions.append({
                "question_number": i + 1,
                "question_text": f"What is {i + 2} + {i + 3}?",
                "question_latex": f"{i + 2} + {i + 3}",
                "difficulty": 0.2 + (i * 0.1),
                "hints": [
                    "Count on your fingers",
                    f"Start from {i + 2} and count up {i + 3} more",
                ],
            })

        return placement_questions[:5]

    def _generate_placement_question(self, topic: Topic, number: int, difficulty: float) -> dict:
        """Generate a template placement question for a topic."""
        question_templates = {
            "arithmetic": {
                "en": "What is {a} + {b}?",
                "hi": "{a} + {b} कितना होता है?",
            },
            "number_sense": {
                "en": "What is the place value of {a} in {b}?",
                "hi": "{b} में {a} का स्थानीय मान क्या है?",
            },
            "geometry": {
                "en": "How many sides does a {shape} have?",
                "hi": "{shape} की कितनी भुजाएँ होती हैं?",
            },
            "measurement": {
                "en": "How many {unit} in 1 {big_unit}?",
                "hi": "1 {big_unit} में कितने {unit} होते हैं?",
            },
        }

        import random
        cat = topic.category or "arithmetic"
        templates = question_templates.get(cat, question_templates["arithmetic"])
        text = templates["en"]

        a = random.randint(1, 20)
        b = random.randint(10, 50)
        text = text.format(a=a, b=a + b, shape="triangle", unit="cm", big_unit="m")

        return {
            "question_number": number,
            "question_text": text,
            "question_latex": None,
            "difficulty": difficulty,
            "hints": [
                "Think about what you learned in class",
                "Take your time and count carefully",
            ],
        }
