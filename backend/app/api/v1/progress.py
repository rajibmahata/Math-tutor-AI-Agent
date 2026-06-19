"""Progress & Analytics API endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{student_id}")
async def get_progress(student_id: str):
    pass  # Phase 1


@router.get("/{student_id}/topics/{topic_id}")
async def get_topic_progress(student_id: str, topic_id: str):
    pass  # Phase 1
