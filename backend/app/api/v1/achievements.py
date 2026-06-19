"""Achievements API endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{student_id}")
async def get_achievements(student_id: str):
    pass  # Phase 1
