"""Test fixtures and configuration for GanitMitra backend tests."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base
from app.config import settings

# Use test-specific settings
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/ganitmitra_test"
    if not settings.database_url.endswith("_test")
    else settings.database_url
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL.replace("+asyncpg", "+asyncpg") if "sqlite" in TEST_DATABASE_URL else TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # For testing without PostgreSQL, use SQLite
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        # Fallback to SQLite for test isolation
        engine = create_async_engine(
            "sqlite+aiosqlite:///./test.db",
            echo=False,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a test database session."""
    test_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with test_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def db(test_engine):
    """Create a clean database session with transaction rollback."""
    test_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with test_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


# =============================================================================
# Model Factories
# =============================================================================
import uuid
from app.models.user import User
from app.models.student import Student
from app.models.session import Session
from app.models.topic import Topic
from app.models.student_topic_progress import StudentTopicProgress
from app.core.security import hash_password


async def create_test_user(db: AsyncSession, **kwargs) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email=kwargs.get("email", "test@example.com"),
        password_hash=hash_password(kwargs.get("password", "password123")),
        full_name=kwargs.get("full_name", "Test Student"),
        role=kwargs.get("role", "student"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


async def create_test_student(db: AsyncSession, user_id: uuid.UUID = None, **kwargs) -> Student:
    """Create a test student profile."""
    if not user_id:
        user = await create_test_user(db)
        user_id = user.id

    student = Student(
        id=uuid.uuid4(),
        user_id=user_id,
        age=kwargs.get("age", 8),
        grade=kwargs.get("grade", "3"),
        preferred_language=kwargs.get("preferred_language", "en"),
        board=kwargs.get("board", "ncert"),
        learning_speed=kwargs.get("learning_speed", 5.0),
        confidence_score=kwargs.get("confidence_score", 0.5),
        total_questions=kwargs.get("total_questions", 50),
        correct_answers=kwargs.get("correct_answers", 38),
        accuracy_rate=kwargs.get("accuracy_rate", 0.76),
        placement_complete=kwargs.get("placement_complete", True),
    )
    db.add(student)
    await db.flush()
    return student


async def create_test_topic(db: AsyncSession, **kwargs) -> Topic:
    """Create a test curriculum topic."""
    topic = Topic(
        id=uuid.uuid4(),
        name_en=kwargs.get("name_en", "Addition"),
        name_hi=kwargs.get("name_hi", "जोड़"),
        name_bn=kwargs.get("name_bn", "যোগ"),
        grade_start=kwargs.get("grade_start", "1"),
        category=kwargs.get("category", "arithmetic"),
        topic_order=kwargs.get("topic_order", 1),
        board=kwargs.get("board", "ncert"),
    )
    db.add(topic)
    await db.flush()
    return topic


async def create_test_session(db: AsyncSession, student_id: uuid.UUID, **kwargs) -> Session:
    """Create a test tutoring session."""
    session = Session(
        id=uuid.uuid4(),
        student_id=student_id,
        session_type=kwargs.get("session_type", "tutoring"),
        language=kwargs.get("language", "en"),
        status=kwargs.get("status", "active"),
        questions_asked=kwargs.get("questions_asked", 5),
        questions_correct=kwargs.get("questions_correct", 4),
    )
    db.add(session)
    await db.flush()
    return session


async def create_test_topic_progress(
    db: AsyncSession, student_id: uuid.UUID, topic_id: uuid.UUID, **kwargs
) -> StudentTopicProgress:
    """Create a test topic progress record."""
    progress = StudentTopicProgress(
        id=uuid.uuid4(),
        student_id=student_id,
        topic_id=topic_id,
        mastery_score=kwargs.get("mastery_score", 0.7),
        questions_attempted=kwargs.get("questions_attempted", 20),
        questions_correct=kwargs.get("questions_correct", 14),
        accuracy_rate=kwargs.get("accuracy_rate", 0.7),
        is_weak=kwargs.get("is_weak", False),
    )
    db.add(progress)
    await db.flush()
    return progress
