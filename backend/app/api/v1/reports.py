"""Parent Report API endpoints."""

from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_parent
from app.models.user import User
from app.services.report import ReportService

router = APIRouter()


@router.get("/{student_id}")
async def get_report(
    student_id: str,
    report_type: str = Query(default="weekly"),
    period_start: str = Query(default=None),
    period_end: str = Query(default=None),
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    """Get or generate a progress report for a student."""
    from app.models.student import Student
    from sqlalchemy import select

    # Verify parent is linked to this student
    result = await db.execute(
        select(Student).where(
            (Student.id == UUID(student_id)) & (Student.parent_id == parent.id)
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("You can only view reports for your linked children")

    # Parse dates
    ps = date.fromisoformat(period_start) if period_start else None
    pe = date.fromisoformat(period_end) if period_end else None

    service = ReportService(db)
    try:
        report = await service.generate_report(
            student_id=UUID(student_id),
            parent_id=parent.id,
            report_type=report_type,
            period_start=ps,
            period_end=pe,
        )
        await db.commit()

        return {
            "id": str(report.id),
            "student_id": str(report.student_id),
            "report_type": report.report_type,
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "summary_text": report.summary_text,
            "key_strengths": report.key_strengths or [],
            "key_weaknesses": report.key_weaknesses or [],
            "recommendations": report.recommendations or [],
            "stats": report.report_data.get("stats", {}),
            "is_read": report.is_read,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        }
    except Exception:
        await db.rollback()
        raise


@router.post("/{report_id}/read")
async def mark_report_read(
    report_id: str,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
):
    """Mark a report as read."""
    service = ReportService(db)
    try:
        await service.mark_read(UUID(report_id))
        await db.commit()
        return {"status": "ok"}
    except Exception:
        await db.rollback()
        raise


@router.get("/{student_id}/list")
async def list_reports(
    student_id: str,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=10, le=50),
):
    """List all reports for a student."""
    service = ReportService(db)
    reports = await service.get_reports(UUID(student_id), limit=limit)

    return {
        "data": [
            {
                "id": str(r.id),
                "report_type": r.report_type,
                "period_start": r.period_start.isoformat(),
                "period_end": r.period_end.isoformat(),
                "summary_snippet": (r.summary_text or "")[:200],
                "is_read": r.is_read,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in reports
        ],
    }
