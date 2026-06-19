"""Unit tests for Student Service and Tutoring Service."""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.student import StudentService
from app.services.tutoring import TutoringService
from app.models.student import Student
from app.models.session import Session
from tests.conftest import (
    create_test_user,
    create_test_student,
    create_test_topic,
    create_test_session,
    create_test_topic_progress,
)


# =============================================================================
# Student Service Tests
# =============================================================================

@pytest.mark.asyncio
async def test_create_student_profile(db: AsyncSession):
    """Creating a student profile should populate all fields."""
    user = await create_test_user(db)

    service = StudentService(db)
    student = await service.create_profile(
        user_id=user.id,
        age=8,
        grade="3",
        preferred_language="hi",
        board="ncert",
    )

    assert student.user_id == user.id
    assert student.age == 8
    assert student.grade == "3"
    assert student.preferred_language == "hi"
    assert student.learning_speed == 5.0
    assert student.confidence_score == 0.5
    assert student.placement_complete is False


@pytest.mark.asyncio
async def test_create_duplicate_profile(db: AsyncSession):
    """Creating a second profile for same user should fail."""
    user = await create_test_user(db)
    service = StudentService(db)

    await service.create_profile(user_id=user.id, age=8, grade="3")

    with pytest.raises(Exception):
        await service.create_profile(user_id=user.id, age=9, grade="4")


@pytest.mark.asyncio
async def test_get_digital_twin(db: AsyncSession):
    """Digital twin should include strengths, weaknesses, and progress."""
    student = await create_test_student(db)
    topic1 = await create_test_topic(db, name_en="Addition", category="arithmetic")
    topic2 = await create_test_topic(db, name_en="Division", category="arithmetic")

    # Create progress records
    await create_test_topic_progress(db, student.id, topic1.id, mastery_score=0.95, is_weak=False)
    await create_test_topic_progress(db, student.id, topic2.id, mastery_score=0.35, is_weak=True)

    service = StudentService(db)
    twin = await service.get_digital_twin(student.id)

    assert twin["grade"] == "3"
    assert twin["preferred_language"] == "en"
    assert len(twin["strengths"]) >= 1
    assert len(twin["weaknesses"]) >= 1
    assert twin["progress_summary"]["topics_mastered"] >= 1
    assert twin["progress_summary"]["grade_progress_pct"] >= 0


@pytest.mark.asyncio
async def test_update_student_profile(db: AsyncSession):
    """Updating student profile should change allowed fields."""
    student = await create_test_student(db)

    service = StudentService(db)
    updated = await service.update_profile(
        student.id,
        preferred_language="bn",
        grade="4",
    )

    assert updated.preferred_language == "bn"
    assert updated.grade == "4"
    assert updated.age == student.age  # Unchanged


@pytest.mark.asyncio
async def test_link_parent(db: AsyncSession):
    """Linking a parent should associate parent with student."""
    student = await create_test_student(db)
    parent = await create_test_user(db, email="parent@test.com", role="parent")

    service = StudentService(db)
    result = await service.link_parent(student.id, "parent@test.com")

    assert result.parent_id == parent.id


@pytest.mark.asyncio
async def test_generate_placement_questions(db: AsyncSession):
    """Placement assessment should generate 5 questions."""
    student = await create_test_student(db)
    # Create a topic for their grade
    await create_test_topic(db, name_en="Test Topic", grade_start="3", category="arithmetic")

    service = StudentService(db)
    questions = await service.generate_placement_questions(student.id)

    assert len(questions) == 5
    for q in questions:
        assert "question_number" in q
        assert "question_text" in q
        assert "difficulty" in q
        assert len(q["hints"]) >= 1


# =============================================================================
# Tutoring Service Tests
# =============================================================================

@pytest.mark.asyncio
async def test_start_session(db: AsyncSession):
    """Starting a session should create it with correct type."""
    student = await create_test_student(db)

    service = TutoringService(db)
    session = await service.start_session(
        student_id=student.id,
        session_type="tutoring",
        language="hi",
    )

    assert session.student_id == student.id
    assert session.session_type == "tutoring"
    assert session.language == "hi"
    assert session.status == "active"
    assert session.started_at is not None


@pytest.mark.asyncio
async def test_end_session(db: AsyncSession):
    """Ending a session should set status and duration."""
    student = await create_test_student(db)
    service = TutoringService(db)

    session = await service.start_session(student_id=student.id)
    ended = await service.end_session(session.id)

    assert ended.status == "completed"
    assert ended.ended_at is not None
    assert ended.duration_seconds is not None


@pytest.mark.asyncio
async def test_save_message(db: AsyncSession):
    """Saving a message should persist it and update session counters."""
    student = await create_test_student(db)
    service = TutoringService(db)
    session = await service.start_session(student_id=student.id)

    msg = await service.save_message(
        session_id=session.id,
        role="student",
        content="What is 12 + 5?",
        content_type="text",
    )

    assert msg.session_id == session.id
    assert msg.role == "student"
    assert msg.content == "What is 12 + 5?"

    # Session counters should update
    from sqlalchemy import select
    result = await db.execute(select(Session).where(Session.id == session.id))
    s = result.scalar_one()
    assert s.questions_asked == 1


@pytest.mark.asyncio
async def test_save_correct_answer_message(db: AsyncSession):
    """Saving a correct answer should increment correct counter."""
    student = await create_test_student(db)
    service = TutoringService(db)
    session = await service.start_session(student_id=student.id)

    await service.save_message(
        session_id=session.id,
        role="student",
        content="17",
        is_correct=True,
    )

    from sqlalchemy import select
    result = await db.execute(select(Session).where(Session.id == session.id))
    s = result.scalar_one()
    assert s.questions_correct == 1


@pytest.mark.asyncio
async def test_get_session_messages(db: AsyncSession):
    """Getting session messages should return messages in order."""
    student = await create_test_student(db)
    service = TutoringService(db)
    session = await service.start_session(student_id=student.id)

    await service.save_message(session_id=session.id, role="student", content="Q1")
    await service.save_message(session_id=session.id, role="teacher", content="A1")
    await service.save_message(session_id=session.id, role="student", content="Q2")

    messages = await service.get_session_messages(session.id, limit=10)
    assert len(messages) == 3
    assert messages[0].content == "Q1"
    assert messages[1].content == "A1"
    assert messages[2].content == "Q2"


@pytest.mark.asyncio
async def test_fallback_hints(db: AsyncSession):
    """Fallback hints should work in all languages."""
    service = TutoringService(db)

    for lang in ["en", "hi", "bn"]:
        hint = service._fallback_hint(1, lang)
        assert hint["type"] == "hint"
        assert len(hint["content"]) > 10
        assert hint["hint_level"] == 1

    hint3 = service._fallback_hint(3, "en")
    assert hint3["hint_level"] == 3
    assert hint3["content"] != service._fallback_hint(1, "en")["content"]


@pytest.mark.asyncio
async def test_update_student_twin_on_answer(db: AsyncSession):
    """Answer evaluation should update student digital twin."""
    student = await create_test_student(db)
    service = TutoringService(db)

    initial_questions = student.total_questions
    initial_confidence = student.confidence_score

    await service._update_student_twin(student, {"is_correct": True, "error_type": None})

    assert student.total_questions == initial_questions + 1
    assert student.correct_answers == 1
    assert student.total_points >= 10
    assert student.confidence_score > initial_confidence  # Confidence should rise


@pytest.mark.asyncio
async def test_update_student_twin_wrong_answer(db: AsyncSession):
    """Wrong answer should still update but reduce confidence."""
    student = await create_test_student(db)
    service = TutoringService(db)

    initial_confidence = student.confidence_score

    await service._update_student_twin(student, {"is_correct": False})

    assert student.total_questions == 1
    assert student.correct_answers == 0
    assert student.confidence_score <= initial_confidence
    assert student.total_points >= 2  # Still gets some points


@pytest.mark.asyncio
async def test_solution_step_parsing(db: AsyncSession):
    """Solution parser should extract numbered steps."""
    service = TutoringService(db)

    content = "Step 1: First do X.\nStep 2: Then do Y.\nFinal step: Z is the answer."
    steps = service._parse_solution_steps(content)

    assert len(steps) >= 2
    assert "First do X" in steps[0]["text"]
    assert "Then do Y" in steps[1]["text"]


@pytest.mark.asyncio
async def test_build_conversation_context(db: AsyncSession):
    """Conversation context builder should format messages correctly."""
    student = await create_test_student(db)
    service = TutoringService(db)
    session = await service.start_session(student_id=student.id)

    msg1 = await service.save_message(session_id=session.id, role="student", content="Hello")
    msg2 = await service.save_message(session_id=session.id, role="teacher", content="Hi there!")

    messages = await service.get_session_messages(session.id)
    context = service._build_conversation_context(messages, "New question")

    assert len(context) >= 2
    assert context[-1]["role"] == "user"
    assert context[-1]["content"] == "New question"
