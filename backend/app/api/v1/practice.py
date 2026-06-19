"""Practice API endpoints: quiz generation, submission, completion."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_practice():
    pass  # Phase 2


@router.get("/{practice_set_id}")
async def get_practice_set(practice_set_id: str):
    pass  # Phase 2


@router.post("/{practice_set_id}/questions/{question_number}/answer")
async def submit_answer(practice_set_id: str, question_number: int):
    pass  # Phase 2


@router.post("/{practice_set_id}/complete")
async def complete_practice(practice_set_id: str):
    pass  # Phase 2
