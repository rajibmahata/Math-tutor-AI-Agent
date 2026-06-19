"""Tutor API endpoints — registration, verification, dashboard, feedback."""

import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tutor import Tutor, TutorDocument, Principal

router = APIRouter()


class TutorRegisterRequest(BaseModel):
    subjects: list = []  # [{"subject":"Math","grade_start":"1","grade_end":"8"}]
    experience_yrs: int = 0
    bio: str = ""


@router.post("/register", status_code=201)
async def register_tutor(
    body: TutorRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register as a tutor."""
    if current_user.role not in ("tutor", "admin"):
        raise HTTPException(status_code=403, detail="Must have tutor or admin role")

    r = await db.execute(select(Tutor).where(Tutor.user_id == current_user.id))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tutor profile already exists")

    tutor = Tutor(
        id=uuid.uuid4(),
        user_id=current_user.id,
        subjects=body.subjects,
        experience_yrs=body.experience_yrs,
        bio=body.bio,
        verification_status="pending",
    )
    db.add(tutor)
    await db.commit()

    return {
        "id": str(tutor.id),
        "user_id": str(tutor.user_id),
        "subjects": tutor.subjects,
        "experience_yrs": tutor.experience_yrs,
        "verification_status": tutor.verification_status,
    }


@router.get("/{tutor_id}")
async def get_tutor(tutor_id: str, db: AsyncSession = Depends(get_db)):
    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    tutor = r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {
        "id": str(tutor.id), "user_id": str(tutor.user_id),
        "subjects": tutor.subjects, "experience_yrs": tutor.experience_yrs,
        "bio": tutor.bio, "verification_status": tutor.verification_status,
        "rating": tutor.rating, "total_students": tutor.total_students,
        "is_active": tutor.is_active,
    }


@router.get("/{tutor_id}/dashboard")
async def tutor_dashboard(tutor_id: str, db: AsyncSession = Depends(get_db)):
    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    tutor = r.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {
        "tutor_id": str(tutor.id), "assigned_students": tutor.total_students or 0,
        "rating": tutor.rating, "verification_status": tutor.verification_status,
    }


@router.post("/{tutor_id}/documents", status_code=201)
async def upload_tutor_document(
    tutor_id: str, file: UploadFile = File(...), doc_type: str = Form(...),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    import os
    tid = uuid.UUID(tutor_id)
    r = await db.execute(select(Tutor).where(Tutor.id == tid))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Tutor not found")
    upload_dir = "/tmp/vidyamitra/tutor_docs"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{tutor_id}_{doc_type}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    doc = TutorDocument(id=uuid.uuid4(), tutor_id=tid, doc_type=doc_type, file_url=file_path)
    db.add(doc)
    await db.commit()
    return {"id": str(doc.id), "doc_type": doc_type, "status": "uploaded"}
