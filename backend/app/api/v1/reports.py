"""Parent Report API endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{student_id}")
async def get_report(student_id: str):
    pass  # Phase 2


@router.post("/{report_id}/read")
async def mark_report_read(report_id: str):
    pass  # Phase 2
