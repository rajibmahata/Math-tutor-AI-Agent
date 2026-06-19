"""Topics & Curriculum API endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_topic_tree():
    pass  # Phase 1


@router.get("/next/{student_id}")
async def get_next_topic(student_id: str):
    pass  # Phase 1
