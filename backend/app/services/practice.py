"""Practice Service — quiz generation, adaptive difficulty, submission."""

import uuid
import logging
import random
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.student import Student
from app.models.topic import Topic
from app.models.practice_set import PracticeSet
from app.models.practice_question import PracticeQuestion
from app.models.student_topic_progress import StudentTopicProgress
from app.routing.router import model_router
from app.config import settings

logger = logging.getLogger(__name__)


class PracticeService:
    """Manages practice quiz generation and adaptive difficulty."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_practice_set(
        self,
        student_id: uuid.UUID,
        topic_id: Optional[uuid.UUID] = None,
        difficulty: str = "adaptive",
        question_count: int = 10,
        language: str = "en",
    ) -> PracticeSet:
        """Generate an adaptive practice quiz."""
        # Load student
        student = await self._get_student(student_id)

        # Determine topic
        if not topic_id:
            topic_id = await self._select_best_topic(student)

        topic = None
        if topic_id:
            topic_result = await self.db.execute(select(Topic).where(Topic.id == topic_id))
            topic = topic_result.scalar_one_or_none()

        # Determine difficulty level
        effective_difficulty = await self._compute_difficulty(
            student, topic_id, difficulty
        )

        # Generate questions via LLM
        questions_data = await self._generate_questions(
            topic=topic,
            student_grade=student.grade,
            difficulty=effective_difficulty,
            count=question_count,
            language=language,
            weak_areas=[],
        )

        # Create practice set
        practice_set = PracticeSet(
            id=uuid.uuid4(),
            student_id=student_id,
            title=f"{topic.name_en if topic else 'Math'} Practice",
            topic_id=topic_id,
            difficulty=difficulty,
            question_count=question_count,
            max_score=question_count,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(practice_set)

        # Create questions
        for i, q_data in enumerate(questions_data):
            question = PracticeQuestion(
                id=uuid.uuid4(),
                practice_set_id=practice_set.id,
                question_number=i + 1,
                question_text=q_data.get("text", f"Question {i + 1}"),
                question_latex=q_data.get("latex"),
                correct_answer=q_data.get("answer", "0"),
                correct_answer_latex=q_data.get("answer_latex"),
                solution_steps=q_data.get("solution", []),
                difficulty=q_data.get("difficulty", effective_difficulty),
                hints=q_data.get("hints", []),
                topic_id=topic_id,
            )
            self.db.add(question)

        await self.db.flush()
        logger.info(f"Practice set generated: {practice_set.id} ({question_count} questions)")

        return practice_set

    async def submit_answer(
        self,
        practice_set_id: uuid.UUID,
        question_number: int,
        answer: str,
        time_taken_seconds: Optional[int] = None,
        hints_used: int = 0,
    ) -> dict:
        """Submit an answer for a practice question."""
        # Load the question
        result = await self.db.execute(
            select(PracticeQuestion).where(
                and_(
                    PracticeQuestion.practice_set_id == practice_set_id,
                    PracticeQuestion.question_number == question_number,
                )
            )
        )
        question = result.scalar_one_or_none()
        if not question:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("PracticeQuestion", f"{practice_set_id}/{question_number}")

        # Evaluate answer
        from app.utils.sympy_verify import verify_answer
        sympy_result = verify_answer(answer, question.question_text)

        # Use LLM for nuanced evaluation if SymPy is inconclusive
        is_correct = sympy_result.get("is_correct", False)
        if is_correct is None:
            # Try semantic comparison via LLM
            is_correct = await self._evaluate_answer_semantic(
                student_answer=answer,
                correct_answer=question.correct_answer,
                question_text=question.question_text,
            )

        # Update question
        question.student_answer = answer
        question.is_correct = is_correct
        question.time_taken_seconds = time_taken_seconds
        question.hints_used = hints_used
        question.answered_at = datetime.now(timezone.utc)

        # Update practice set status
        result = await self.db.execute(
            select(PracticeSet).where(PracticeSet.id == practice_set_id)
        )
        practice_set = result.scalar_one_or_none()
        if practice_set:
            practice_set.status = "in_progress"
            practice_set.started_at = practice_set.started_at or datetime.now(timezone.utc)

        await self.db.flush()

        return {
            "is_correct": bool(is_correct),
            "correct_answer": question.correct_answer,
            "solution": question.solution_steps,
            "points_earned": 10 if is_correct else 2,
        }

    async def complete_practice(self, practice_set_id: uuid.UUID) -> dict:
        """Complete a practice set and compute results."""
        result = await self.db.execute(
            select(PracticeSet).where(PracticeSet.id == practice_set_id)
        )
        practice_set = result.scalar_one_or_none()
        if not practice_set:
            raise NotFoundError("PracticeSet", str(practice_set_id))

        # Count correct
        questions_result = await self.db.execute(
            select(PracticeQuestion).where(
                PracticeQuestion.practice_set_id == practice_set_id
            )
        )
        questions = questions_result.scalars().all()

        correct_count = sum(1 for q in questions if q.is_correct)
        practice_set.score = correct_count
        practice_set.status = "completed"
        practice_set.completed_at = datetime.now(timezone.utc)

        # Update student topic progress
        if practice_set.topic_id:
            await self._update_topic_progress(
                student_id=practice_set.student_id,
                topic_id=practice_set.topic_id,
                correct=correct_count,
                total=len(questions),
            )

        # Update student stats
        student = await self._get_student(practice_set.student_id)
        if student:
            student.total_questions += len(questions)
            student.correct_answers += correct_count
            student.accuracy_rate = student.correct_answers / max(student.total_questions, 1)
            student.total_points += correct_count * 10 + (len(questions) - correct_count) * 2
            student.total_sessions += 1

        await self.db.flush()

        # Generate solution feedback for incorrect questions
        incorrect_breakdown = []
        for q in questions:
            if not q.is_correct and q.student_answer:
                incorrect_breakdown.append({
                    "question_number": q.question_number,
                    "your_answer": q.student_answer,
                    "correct_answer": q.correct_answer,
                    "topic": str(q.topic_id) if q.topic_id else None,
                })

        return {
            "id": str(practice_set.id),
            "score": correct_count,
            "max_score": len(questions),
            "accuracy": round(correct_count / max(len(questions), 1), 2),
            "topics_updated": [],
            "points_earned": correct_count * 10 + (len(questions) - correct_count) * 2,
            "incorrect_breakdown": incorrect_breakdown,
        }

    # =========================================================================
    # Internal Methods
    # =========================================================================

    async def _get_student(self, student_id: uuid.UUID) -> Optional[Student]:
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        return result.scalar_one_or_none()

    async def _select_best_topic(self, student: Student) -> Optional[uuid.UUID]:
        """Select the best topic for practice based on student weaknesses."""
        # Priority 1: Weak topics
        result = await self.db.execute(
            select(StudentTopicProgress)
            .where(
                and_(
                    StudentTopicProgress.student_id == student.id,
                    StudentTopicProgress.is_weak == True,
                )
            )
            .order_by(StudentTopicProgress.mastery_score.asc())
            .limit(1)
        )
        weak_progress = result.scalar_one_or_none()
        if weak_progress:
            return weak_progress.topic_id

        # Priority 2: In-progress topics
        result = await self.db.execute(
            select(StudentTopicProgress)
            .where(
                and_(
                    StudentTopicProgress.student_id == student.id,
                    StudentTopicProgress.mastery_score > 0,
                    StudentTopicProgress.mastery_score < 0.85,
                )
            )
            .order_by(StudentTopicProgress.mastery_score.asc())
            .limit(1)
        )
        progress = result.scalar_one_or_none()
        if progress:
            return progress.topic_id

        # Priority 3: New topics for current grade
        mastered_ids_result = await self.db.execute(
            select(StudentTopicProgress.topic_id).where(
                and_(
                    StudentTopicProgress.student_id == student.id,
                    StudentTopicProgress.mastery_score >= 0.85,
                )
            )
        )
        mastered_ids = {r[0] for r in mastered_ids_result.all()}

        topic_query = select(Topic).where(Topic.grade_start == student.grade)
        if mastered_ids:
            topic_query = topic_query.where(Topic.id.notin_(mastered_ids))
        topic_result = await self.db.execute(topic_query.order_by(Topic.topic_order).limit(1))
        topic = topic_result.scalar_one_or_none()
        return topic.id if topic else None

    async def _compute_difficulty(
        self,
        student: Student,
        topic_id: Optional[uuid.UUID],
        requested: str,
    ) -> float:
        """Compute the optimal difficulty for a student on a topic."""
        if requested != "adaptive":
            difficulty_map = {"easy": 0.3, "medium": 0.6, "hard": 0.85}
            return difficulty_map.get(requested, 0.5)

        if not topic_id:
            return 0.5

        # Load topic progress
        result = await self.db.execute(
            select(StudentTopicProgress).where(
                and_(
                    StudentTopicProgress.student_id == student.id,
                    StudentTopicProgress.topic_id == topic_id,
                )
            )
        )
        progress = result.scalar_one_or_none()

        if not progress or progress.questions_attempted < 3:
            return 0.35  # Start easy

        # Target 80% success rate
        if progress.accuracy_rate >= 0.85:
            # Student is doing well — increase difficulty
            return min(0.9, progress.mastery_score + 0.15)
        elif progress.accuracy_rate < 0.5:
            # Student is struggling — decrease difficulty
            return max(0.2, progress.mastery_score - 0.1)
        else:
            # Keep current level
            return progress.mastery_score

    async def _generate_questions(
        self,
        topic: Optional[Topic],
        student_grade: str,
        difficulty: float,
        count: int,
        language: str,
        weak_areas: list[str],
    ) -> list[dict]:
        """Generate practice questions via LLM or templates."""
        if topic and topic.name_en:
            topic_name = topic.name_en
        else:
            topic_name = f"Grade {student_grade} Math"

        system_prompt = f"""Generate {count} math practice questions for a Grade {student_grade} student.
Topic: {topic_name}
Difficulty: {difficulty:.1f} (0=easy, 1=hard)
Language: {language}
Target success rate: 80%

For each question, provide:
1. Question text in {language}
2. LaTeX representation (if applicable) 
3. Correct answer
4. 3 progressive hints (from gentle to specific)
5. Step-by-step solution
6. Difficulty score (0.0-1.0)

Format as JSON array of question objects."""

        try:
            response = await model_router.route(
                task_type="question_generation",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate {count} questions about {topic_name} for Grade {student_grade} in {language}."},
                ],
                language=language,
            )

            # Parse JSON response
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            elif "```json" in content:
                content = content.split("```json\n", 1)[1].split("```", 1)[0]

            import json as _json
            questions = _json.loads(content)
            if isinstance(questions, list):
                return questions[:count]
        except Exception as e:
            logger.warning(f"LLM question generation failed, using templates: {e}")

        # Fallback: template questions
        return self._generate_template_questions(topic_name, student_grade, difficulty, count, language)

    def _generate_template_questions(
        self,
        topic_name: str,
        grade: str,
        difficulty: float,
        count: int,
        language: str,
    ) -> list[dict]:
        """Generate template questions when LLM is unavailable."""
        templates = []
        for i in range(count):
            a = random.randint(1, 20 + int(difficulty * 30))
            b = random.randint(1, 10 + int(difficulty * 15))
            op = random.choice(["+", "-", "×"])

            if op == "+":
                answer = a + b
            elif op == "-":
                if a < b:
                    a, b = b, a
                answer = a - b
            else:
                answer = a * b

            text_map = {
                "en": f"What is {a} {op} {b}?",
                "hi": f"{a} {op} {b} कितना होता है?",
                "bn": f"{a} {op} {b} কত হয়?",
            }
            templates.append({
                "text": text_map.get(language, text_map["en"]),
                "latex": f"{a} {op if op != '×' else '\\times'} {b}",
                "answer": str(answer),
                "difficulty": difficulty,
                "hints": [
                    f"Think about the {'sum' if op == '+' else 'difference' if op == '-' else 'product'}",
                    f"Break it down: {a} and {b}",
                    f"Try calculating: the answer is around {answer - 2} to {answer + 2}",
                ],
                "solution": {
                    "steps": [
                        {"step": 1, "text": f"Identify the operation: {op}", "latex": None},
                        {"step": 2, "text": f"Calculate: {a} {op} {b} = {answer}", "latex": f"{a} {op if op != '×' else '\\times'} {b} = {answer}"},
                    ]
                },
            })

        return templates

    async def _evaluate_answer_semantic(
        self,
        student_answer: str,
        correct_answer: str,
        question_text: str,
    ) -> bool:
        """Use LLM for semantic answer comparison."""
        try:
            response = await model_router.route(
                task_type="answer_evaluation",
                messages=[
                    {"role": "system", "content": f"""Determine if the student's answer is mathematically equivalent to the correct answer.
Question: {question_text}
Correct Answer: {correct_answer}
Student Answer: {student_answer}

Respond with ONLY 'true' or 'false'."""},
                ],
            )
            return "true" in response.content.strip().lower()
        except Exception:
            return student_answer.strip() == correct_answer.strip()

    async def _update_topic_progress(
        self,
        student_id: uuid.UUID,
        topic_id: uuid.UUID,
        correct: int,
        total: int,
    ):
        """Update student topic progress after a practice set."""
        result = await self.db.execute(
            select(StudentTopicProgress).where(
                and_(
                    StudentTopicProgress.student_id == student_id,
                    StudentTopicProgress.topic_id == topic_id,
                )
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = StudentTopicProgress(
                id=uuid.uuid4(),
                student_id=student_id,
                topic_id=topic_id,
            )
            self.db.add(progress)

        progress.questions_attempted += total
        progress.questions_correct += correct
        progress.accuracy_rate = progress.questions_correct / max(progress.questions_attempted, 1)
        progress.last_attempted_at = datetime.now(timezone.utc)
        progress.times_reviewed += 1

        # Recompute mastery
        raw = progress.accuracy_rate
        recent = correct / max(total, 1)
        progress.mastery_score = min(1.0, raw * 0.6 + recent * 0.4)

        # Mastery threshold
        if progress.mastery_score >= 0.85 and not progress.mastered_at:
            progress.mastered_at = datetime.now(timezone.utc)
            progress.is_weak = False
        elif progress.mastery_score < 0.5 and progress.questions_attempted >= 5:
            progress.is_weak = True

        await self.db.flush()
