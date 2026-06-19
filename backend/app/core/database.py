"""Database engine, session, and base model configuration.
Supports both PostgreSQL (production) and SQLite (local dev)."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Determine if using SQLite
is_sqlite = "sqlite" in settings.database_url

# SQLite needs check_same_thread=False
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=1 if is_sqlite else 20,
    max_overflow=0 if is_sqlite else 10,
    pool_pre_ping=not is_sqlite,
    connect_args=connect_args,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency: yield an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables. For dev/CI; production uses Alembic."""
    # Force import all models so they register with Base.metadata
    from app.models import (
        User, RefreshToken, Student, Session, Message, Assessment,
        Topic, TopicPrerequisite, StudentTopicProgress,
        PracticeSet, PracticeQuestion, ParentReport,
        StudentAchievement, KnowledgeDocument,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
