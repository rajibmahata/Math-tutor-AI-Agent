"""Student API endpoints — full implementation."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_student
from app.services.student import StudentService
from app.models.user import User
from app.models.student import Student
from app.schemas.common import (
    StudentCreateRequest,
    StudentUpdateRequest,
    LinkParentRequest,
    StudentResponse,
)

router = APIRouter()


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(
    body: StudentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a student profile for the current user."""
    service = StudentService(db)
    try:
        student = await service.create_profile(
            user_id=current_user.id,
            age=body.age,
            grade=body.grade,
            preferred_language=body.preferred_language,
            board=body.board,
        )
        await db.commit()
        # Return fresh with relationships
        twin = await service.get_digital_twin(student.id)
        return twin
    except Exception:
        await db.rollback()
        raise


@router.get("/{student_id}")
async def get_student(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get student digital twin profile."""
    from uuid import UUID

    # Authorize: student can only see their own data
    service = StudentService(db)
    student = await service.get_profile(UUID(student_id))
    if not student:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Student", student_id)

    # Check access: own profile, parent of this student, or admin
    if current_user.role == "student" and student.user_id != current_user.id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("You can only view your own profile")

    if current_user.role == "parent" and student.parent_id != current_user.id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("You can only view your linked children's profiles")

    twin = await service.get_digital_twin(UUID(student_id))
    return twin


@router.patch("/{student_id}")
async def update_student(
    student_id: str,
    body: StudentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update student profile fields."""
    from uuid import UUID

    service = StudentService(db)
    student = await service.get_profile(UUID(student_id))
    if not student:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Student", student_id)

    if student.user_id != current_user.id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError()

    try:
        updated = await service.update_profile(
            UUID(student_id),
            age=body.age,
            grade=body.grade,
            preferred_language=body.preferred_language,
            board=body.board,
        )
        await db.commit()
        twin = await service.get_digital_twin(updated.id)
        return twin
    except Exception:
        await db.rollback()
        raise


@router.post("/{student_id}/placement")
async def take_placement(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and return placement assessment questions."""
    from uuid import UUID

    service = StudentService(db)
    questions = await service.generate_placement_questions(UUID(student_id))

    # Create a placement session
    from app.models.session import Session
    import uuid as _uuid

    session = Session(
        id=_uuid.uuid4(),
        student_id=UUID(student_id),
        session_type="placement",
        language="en",
        status="active",
    )
    db.add(session)
    await db.flush()
    await db.commit()

    return {
        "session_id": str(session.id),
        "questions": questions,
    }


@router.post("/{student_id}/link-parent")
async def link_parent(
    student_id: str,
    body: LinkParentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Link a parent to this student."""
    from uuid import UUID

    service = StudentService(db)
    try:
        student = await service.link_parent(
            UUID(student_id),
            body.parent_email,
            body.relationship,
        )
        await db.commit()
        return {"linked": True, "parent_email": body.parent_email}
    except Exception:
        await db.rollback()
        raise
