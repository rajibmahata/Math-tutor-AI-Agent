"""Tutoring Service — session management, agent orchestration, WebSocket handling."""

import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional, AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import WebSocket, WebSocketDisconnect

from app.models.student import Student
from app.models.user import User
from app.models.session import Session
from app.models.message import Message
from app.models.topic import Topic
from app.models.student_topic_progress import StudentTopicProgress
from app.config import settings
from app.routing.router import model_router

logger = logging.getLogger(__name__)


class TutoringService:
    """Orchestrates tutoring sessions — the heart of GanitMitra."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_session(
        self,
        student_id: uuid.UUID,
        session_type: str = "tutoring",
        language: str = "en",
        topic_id: Optional[uuid.UUID] = None,
    ) -> Session:
        """Create a new tutoring session."""
        session = Session(
            id=uuid.uuid4(),
            student_id=student_id,
            session_type=session_type,
            language=language,
            topic_id=topic_id,
            status="active",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(session)

        # Update student's last session timestamp
        student_result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()
        if student:
            student.last_session_at = datetime.now(timezone.utc)
            student.total_sessions += 1

        await self.db.flush()
        logger.info(f"Session started: {session.id} (type={session_type}, lang={language})")
        return session

    async def end_session(self, session_id: uuid.UUID) -> Session:
        """End a tutoring session with metrics."""
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Session", str(session_id))

        session.status = "completed"
        session.ended_at = datetime.now(timezone.utc)

        if session.started_at:
            session.duration_seconds = int(
                (session.ended_at - session.started_at).total_seconds()
            )

        await self.db.flush()
        return session

    async def save_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        content_type: str = "text",
        hint_level: Optional[int] = None,
        is_correct: Optional[bool] = None,
        math_expression: Optional[str] = None,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None,
        latency_ms: Optional[int] = None,
    ) -> Message:
        """Save a message to a session."""
        message = Message(
            id=uuid.uuid4(),
            session_id=session_id,
            role=role,
            content=content,
            content_type=content_type,
            hint_level=hint_level,
            is_correct=is_correct,
            math_expression=math_expression,
            tokens_used=tokens_used,
            model_used=model_used,
            latency_ms=latency_ms,
        )
        self.db.add(message)

        # Update session counters
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.questions_asked += 1
            if is_correct:
                session.questions_correct += 1
            if hint_level and hint_level > 0:
                session.hints_used += 1

        await self.db.flush()
        return message

    async def get_session_messages(
        self,
        session_id: uuid.UUID,
        limit: int = 50,
    ) -> list[Message]:
        """Get messages for a session."""
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    # =========================================================================
    # Teacher Agent — Hint → Guide → Solve
    # =========================================================================

    async def process_student_message(
        self,
        session_id: uuid.UUID,
        student_message: str,
        student: Student,
        language: str = "en",
    ) -> dict:
        """
        Process a student message through the AI agent pipeline.
        Returns a response dict for WebSocket delivery.
        """
        # Load session context
        recent_messages = await self.get_session_messages(session_id, limit=10)
        conversation = self._build_conversation_context(recent_messages, student_message)

        # Step 1: Classify intent
        intent = await self._classify_intent(student_message, language, student.grade)

        if intent == "greeting":
            response_data = await self._handle_greeting(student, language)
        elif intent == "learn":
            response_data = await self._handle_learning(
                student_message, student, conversation, language
            )
        elif intent == "progress":
            response_data = await self._handle_progress_query(student, language)
        else:
            response_data = await self._handle_learning(
                student_message, student, conversation, language
            )

        # Save teacher message
        await self.save_message(
            session_id=session_id,
            role="teacher",
            content=response_data.get("content", ""),
            content_type=response_data.get("type", "text"),
            hint_level=response_data.get("hint_level"),
            tokens_used=response_data.get("tokens_used"),
            model_used=response_data.get("model_used"),
            latency_ms=response_data.get("latency_ms"),
        )

        return response_data

    async def process_student_answer(
        self,
        session_id: uuid.UUID,
        student_answer: str,
        student: Student,
        language: str = "en",
    ) -> dict:
        """
        Evaluate a student's answer through the Assessment Agent.
        Returns evaluation + motivation.
        """
        # Save student answer
        msg = await self.save_message(
            session_id=session_id,
            role="student",
            content=student_answer,
            content_type="text",
        )

        # Get recent context for evaluation — find the student's ORIGINAL question
        recent = await self.get_session_messages(session_id, limit=10)
        last_question = None
        # Scan backwards to find the student's math question (before any hints/answers)
        for m in reversed(recent):
            if m.role == "student" and m.content_type == "text":
                # Use the first student message that looks like a question
                if any(c.isdigit() for c in m.content) or len(m.content) > 10:
                    last_question = m.content
                    break
        # Fallback: use the most recent student message that isn't the current answer
        if not last_question:
            for m in reversed(recent):
                if m.role == "student" and m.content != student_answer:
                    last_question = m.content
                    break

        # Evaluate the answer
        evaluation = await self._evaluate_answer(
            student_answer=student_answer,
            question=last_question or "",
            student_grade=student.grade,
            language=language,
        )

        # Update message with evaluation
        msg.is_correct = evaluation.get("is_correct", False)
        msg.math_expression = student_answer

        # Update student digital twin
        await self._update_student_twin(student, evaluation)

        # Generate motivation
        motivation = await self._generate_motivation(
            student=student,
            is_correct=evaluation.get("is_correct", False),
            language=language,
        )

        # Save motivation message
        await self.save_message(
            session_id=session_id,
            role="teacher",
            content=motivation,
            content_type="encouragement",
        )

        return {
            "type": "feedback",
            "is_correct": evaluation.get("is_correct", False),
            "content": evaluation.get("feedback", motivation),
            "points_earned": 10 if evaluation.get("is_correct") else 2,
            "motivation": motivation,
        }

    async def generate_hint(
        self,
        session_id: uuid.UUID,
        hint_level: int,
        student: Student,
        language: str = "en",
    ) -> dict:
        """Generate a progressive hint (levels 1-3)."""
        recent = await self.get_session_messages(session_id, limit=5)
        conversation = self._build_conversation_context(recent)

        prompts = {
            1: f"Give a gentle conceptual hint for this math problem. Do NOT give the answer. Language: {language}.",
            2: f"Give a more specific hint. Point toward the method without revealing the answer. Language: {language}.",
            3: f"Give a very specific hint that almost reveals the method, but still let the student make the final step. Language: {language}.",
        }

        system_prompt = prompts.get(hint_level, prompts[1])

        messages = [
            {"role": "system", "content": f"""You are a patient math teacher for Grade {student.grade}.
{system_prompt}
Student preferred language: {language}. Respond in {language}.
Keep hints concise (2-3 sentences).""" },
            *conversation,
        ]

        try:
            response = await model_router.route(
                task_type="hint_generation",
                messages=messages,
                language=language,
            )
            return {
                "type": "hint",
                "content": response.content,
                "hint_level": hint_level,
                "tokens_used": response.tokens_used,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
            }
        except Exception as e:
            logger.error(f"Hint generation failed: {e}")
            return self._fallback_hint(hint_level, language)

    async def generate_solution(
        self,
        session_id: uuid.UUID,
        student: Student,
        language: str = "en",
    ) -> dict:
        """Generate a full step-by-step solution."""
        recent = await self.get_session_messages(session_id, limit=10)
        conversation = self._build_conversation_context(recent)

        system_prompt = f"""You are a math teacher. A Grade {student.grade} student needs a step-by-step solution.
Break the solution into clear, numbered steps.
Use simple language appropriate for Grade {student.grade}.
Respond in {language}.
Format each step as a separate, clear explanation."""

        messages = [
            {"role": "system", "content": system_prompt},
            *conversation,
            {"role": "system", "content": "Now provide the step-by-step solution."},
        ]

        try:
            response = await model_router.route(
                task_type="step_by_step",
                messages=messages,
                language=language,
            )
            # Parse steps from response
            steps = self._parse_solution_steps(response.content)
            return {
                "type": "solution",
                "steps": steps,
                "tokens_used": response.tokens_used,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
            }
        except Exception as e:
            logger.error(f"Solution generation failed: {e}")
            return {
                "type": "solution",
                "steps": [{"step": 1, "text": "Let me help you work through this step by step.", "latex": None}],
            }

    # =========================================================================
    # Internal Agent Methods
    # =========================================================================

    async def _classify_intent(self, message: str, language: str, grade: str) -> str:
        """Classify student message intent."""
        messages = [
            {"role": "system", "content": f"""Classify this student message as:
- greeting: hello, thanks, how are you, bye
- learn: a math question, asking for help with a problem
- progress: asking about their progress, scores, achievements

Student grade: {grade}. Language: {language}.
Respond with exactly ONE word: greeting, learn, or progress.""" },
            {"role": "user", "content": message},
        ]

        try:
            response = await model_router.route(
                task_type="intent_classify",
                messages=messages,
                language=language,
            )
            intent = response.content.strip().lower()
            return intent if intent in ("greeting", "learn", "progress") else "learn"
        except Exception:
            return "learn"

    async def _handle_greeting(self, student: Student, language: str) -> dict:
        """Handle a greeting/chat message."""
        student_name = ""
        # Get student name from user table
        result = await self.db.execute(select(User).where(User.id == student.user_id))
        user = result.scalar_one_or_none()
        if user:
            student_name = user.full_name

        greetings = {
            "en": f"Hi {student_name}! Ready to learn some math today? What would you like to practice? 😊",
            "hi": f"नमस्ते {student_name}! आज क्या सीखना चाहोगे? 😊",
            "bn": f"নমস্কার {student_name}! আজ কী শিখতে চাও? 😊",
        }

        content = greetings.get(language, greetings["en"])

        try:
            response = await model_router.route(
                task_type="greeting",
                messages=[
                    {"role": "system", "content": f"Greet a Grade {student.grade} math student warmly in {language}."},
                    {"role": "user", "content": "Hi!"},
                ],
                language=language,
            )
            content = response.content
        except Exception:
            pass

        return {"type": "text", "content": content}

    async def _handle_learning(
        self,
        message: str,
        student: Student,
        conversation: list[dict],
        language: str,
    ) -> dict:
        """Handle a learning/math question — provide a hint."""
        system_prompt = f"""You are GanitMitra, a patient math teacher for a Grade {student.grade} student.
Teach in {language}. Use simple, age-appropriate language.

## MANDATORY RULES:
1. NEVER give the final answer directly.
2. Start with a HINT that guides thinking.
3. Encourage the student to try.
4. Keep it short (2-3 sentences).

Student grade: {student.grade}
Respond in {language}."""

        messages = [
            {"role": "system", "content": system_prompt},
            *conversation[-6:],  # Last 6 messages for context
        ]

        try:
            response = await model_router.route(
                task_type="hint_generation",
                messages=messages,
                language=language,
            )
            return {
                "type": "hint",
                "content": response.content,
                "hint_level": 1,
                "tokens_used": response.tokens_used,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
            }
        except Exception as e:
            logger.error(f"Learning handler failed: {e}")
            return {
                "type": "hint",
                "content": self._fallback_hint(1, language)["content"],
                "hint_level": 1,
            }

    async def _handle_progress_query(self, student: Student, language: str) -> dict:
        """Handle a progress query."""
        try:
            response = await model_router.route(
                task_type="encouragement",
                messages=[
                    {"role": "system", "content": f"Tell a Grade {student.grade} student about their progress in {language}."},
                    {"role": "user", "content": f"My accuracy is {student.accuracy_rate:.0%}, I have {student.total_points} points and have answered {student.total_questions} questions."},
                ],
                language=language,
            )
            content = response.content
        except Exception:
            templates = {
                "en": f"You've answered {student.total_questions} questions with {student.accuracy_rate:.0%} accuracy! You've earned {student.total_points} points. Keep it up! 🔥",
                "hi": f"आपने {student.total_questions} सवालों के जवाब दिए हैं, {student.accuracy_rate:.0%} सही! आपके {student.total_points} पॉइंट्स हैं। बढ़िया चल रहा है! 🔥",
                "bn": f"তুমি {student.total_questions}টি প্রশ্নের উত্তর দিয়েছো, {student.accuracy_rate:.0%} সঠিক! তোমার {student.total_points} পয়েন্ট আছে। দারুণ চলছে! 🔥",
            }
            content = templates.get(language, templates["en"])

        return {"type": "text", "content": content}

    async def _evaluate_answer(
        self,
        student_answer: str,
        question: str,
        student_grade: str,
        language: str,
    ) -> dict:
        """Evaluate a student's answer using the Assessment Agent."""
        # Try SymPy verification for numeric answers
        from app.utils.sympy_verify import verify_answer

        sympy_result = verify_answer(student_answer, question)

        system_prompt = f"""Evaluate this student's math answer.
Grade: {student_grade}. Language: {language}.

Question: {question}
Student Answer: {student_answer}
SymPy computation says: {sympy_result}

Determine if the answer is correct. Consider:
- Mathematical equivalence (not just exact string match)
- Partial credit for right method but wrong calculation
- Conceptual understanding even if answer is slightly off

Respond in JSON format:
{{"is_correct": true/false, "is_partial": true/false, "error_type": "arithmetic|conceptual|careless|sign_error|order_of_ops|null", "feedback": "constructive feedback in {language}", "misconception": "what student doesn't understand"}}"""

        try:
            response = await model_router.route(
                task_type="answer_evaluation",
                messages=[
                    {"role": "system", "content": system_prompt},
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
            return _json.loads(content)
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                "is_correct": sympy_result.get("is_correct", False),
                "is_partial": False,
                "error_type": None,
                "feedback": "Good effort! Let me help you with this one.",
                "misconception": None,
            }

    async def _generate_motivation(
        self,
        student: Student,
        is_correct: bool,
        language: str,
    ) -> str:
        """Generate a motivational message."""
        try:
            system_prompt = f"""Motivate a Grade {student.grade} student in {language}.
They just got the answer {'CORRECT' if is_correct else 'INCORRECT'}.
Be encouraging. Keep it short (1-2 sentences). Use their language."""

            response = await model_router.route(
                task_type="encouragement",
                messages=[
                    {"role": "system", "content": system_prompt},
                ],
                language=language,
            )
            return response.content
        except Exception:
            if is_correct:
                return {"en": "⭐ Great job! Keep it up!", "hi": "⭐ शाबाश! बहुत अच्छे!", "bn": "⭐ দারুণ! এগিয়ে যাও!"}.get(language, "⭐ Great job!")
            return {"en": "Good try! Let's learn from this.", "hi": "अच्छी कोशिश! चलो इससे सीखते हैं।", "bn": "ভালো চেষ্টা! এখান থেকে শিখি।"}.get(language, "Good try!")

    async def _update_student_twin(self, student: Student, evaluation: dict):
        """Update the student digital twin after an answer."""
        is_correct = evaluation.get("is_correct", False)
        student.total_questions += 1

        if is_correct:
            student.correct_answers += 1

        student.accuracy_rate = student.correct_answers / max(student.total_questions, 1)

        # Boost confidence on correct answers, slight dip on wrong
        delta = 0.02 if is_correct else -0.01
        student.confidence_score = max(0.1, min(1.0, student.confidence_score + delta))

        # Add points
        points = 10 if is_correct else 2
        student.total_points += points

        # Update learning speed (slow adaptation)
        if student.total_questions > 10:
            if student.accuracy_rate > 0.8:
                student.learning_speed = min(10.0, student.learning_speed + 0.1)
            elif student.accuracy_rate < 0.5:
                student.learning_speed = max(1.0, student.learning_speed - 0.1)

        # Update streak (assume daily)
        today = datetime.now(timezone.utc).date()
        if student.last_session_at and student.last_session_at.date() == today:
            pass  # Already counted today
        elif student.last_session_at and (today - student.last_session_at.date()).days == 1:
            student.current_streak += 1
            student.longest_streak = max(student.longest_streak, student.current_streak)
        elif student.last_session_at and (today - student.last_session_at.date()).days > 1:
            student.current_streak = 1
        else:
            student.current_streak = 1

        # Check for achievements
        from app.models.student_achievement import StudentAchievement
        achievements_to_check = [
            ("streak_3", student.current_streak >= 3),
            ("streak_7", student.current_streak >= 7),
            ("questions_100", student.total_questions >= 100),
            ("questions_500", student.total_questions >= 500),
            ("accuracy_80", student.accuracy_rate >= 0.8 and student.total_questions >= 20),
            ("accuracy_90", student.accuracy_rate >= 0.9 and student.total_questions >= 50),
        ]

        for ach_type, earned in achievements_to_check:
            if earned:
                result = await self.db.execute(
                    select(StudentAchievement).where(
                        (StudentAchievement.student_id == student.id)
                        & (StudentAchievement.achievement_type == ach_type)
                    )
                )
                if not result.scalar_one_or_none():
                    ach_names = {
                        "streak_3": ("3-Day Streak! 🔥", "3-दिन की स्ट्रीक! 🔥", "৩ দিনের স্ট্রিক! 🔥"),
                        "streak_7": ("7-Day Streak! 🔥🔥", "7-दिन की स्ट्रीक! 🔥🔥", "৭ দিনের স্ট্রিক! 🔥🔥"),
                        "questions_100": ("Century! 💯", "सौ सवाल! 💯", "শতক! 💯"),
                        "questions_500": ("500 Club! 🏆", "500 क्लब! 🏆", "৫০০ ক্লাব! 🏆"),
                        "accuracy_80": ("Sharpshooter! 🎯", "निशानेबाज़! 🎯", "লক্ষ্যভেদী! 🎯"),
                        "accuracy_90": ("Math Wizard! 🧙", "गणित जादूगर! 🧙", "গণিত জাদুকর! 🧙"),
                    }
                    titles = ach_names.get(ach_type, (ach_type, ach_type, ach_type))
                    achievement = StudentAchievement(
                        id=uuid.uuid4(),
                        student_id=student.id,
                        achievement_type=ach_type,
                        title_en=titles[0],
                        title_hi=titles[1],
                        title_bn=titles[2],
                    )
                    self.db.add(achievement)

    # =========================================================================
    # Helpers
    # =========================================================================

    def _build_conversation_context(
        self,
        messages: list[Message],
        current_message: str = "",
    ) -> list[dict]:
        """Build conversation context for the LLM."""
        conversation = []
        for msg in messages[-8:]:  # Last 8 messages
            role = "assistant" if msg.role == "teacher" else "user"
            conversation.append({"role": role, "content": msg.content})
        if current_message:
            conversation.append({"role": "user", "content": current_message})
        return conversation

    def _parse_solution_steps(self, content: str) -> list[dict]:
        """Parse a solution response into numbered steps."""
        steps = []
        lines = content.strip().split("\n")
        step_num = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Try to detect step patterns
            if line[0].isdigit() and (". " in line or ") " in line):
                step_num += 1
                text = line.split(". ", 1)[-1] if ". " in line else line.split(") ", 1)[-1]
                steps.append({"step": step_num, "text": text, "latex": None})
            elif line.startswith("Step") or line.startswith("Final"):
                step_num += 1
                steps.append({"step": step_num, "text": line, "latex": None})
            elif steps and step_num > 0:
                # Continuation of previous step
                steps[-1]["text"] += " " + line

        if not steps:
            steps = [{"step": 1, "text": content, "latex": None}]

        return steps

    def _fallback_hint(self, hint_level: int, language: str) -> dict:
        """Fallback hints when LLM is unavailable."""
        hints = {
            1: {
                "en": "Think about what operation you need to use here. Look at the numbers carefully.",
                "hi": "सोचो कि यहाँ कौन सी गणित क्रिया का उपयोग करना है। संख्याओं को ध्यान से देखो।",
                "bn": "চিন্তা করো এখানে কোন গাণিতিক ক্রিয়া ব্যবহার করতে হবে। সংখ্যাগুলো ভালো করে দেখো।",
            },
            2: {
                "en": "Try breaking this down into smaller steps. What's the first thing you would calculate?",
                "hi": "इसे छोटे-छोटे हिस्सों में तोड़कर देखो। सबसे पहले क्या निकालोगे?",
                "bn": "এটাকে ছোট ছোট ধাপে ভাগ করো। সবার আগে কী বের করবে?",
            },
            3: {
                "en": "You're almost there! The key is to remember that... Check the signs carefully.",
                "hi": "बस करीब हो! ध्यान रखो कि... चिह्नों को ध्यान से देखो।",
                "bn": "একদম কাছাকাছি! মনে রেখো যে... চিহ্নগুলো ভালো করে দেখো।",
            },
        }
        level_hints = hints.get(hint_level, hints[1])
        content = level_hints.get(language, level_hints["en"])
        return {"type": "hint", "content": content, "hint_level": hint_level}
