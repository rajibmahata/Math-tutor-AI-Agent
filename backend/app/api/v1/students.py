"""Student API endpoints: profile CRUD, placement, parent linking."""

from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def create_student():
    pass  # Phase 1


@router.get("/{student_id}")
async def get_student(student_id: str):
    pass  # Phase 1


@router.patch("/{student_id}")
async def update_student(student_id: str):
    pass  # Phase 1


@router.post("/{student_id}/placement")
async def take_placement(student_id: str):
    pass  # Phase 1


@router.post("/{student_id}/link-parent")
async def link_parent(student_id: str):
    pass  # Phase 1
