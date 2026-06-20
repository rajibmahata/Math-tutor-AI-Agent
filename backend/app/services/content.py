"""Content generation service — PDF ingestion, AI lesson creation, and validation workflow."""

import io
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.content import SourceDocument, ContentLesson, ContentReview
from app.models.notification import NotificationType, NotificationPriority
from app.services.notification import notification_service
from app.routing.router import model_router

logger = logging.getLogger(__name__)

# Languages we generate content for
SUPPORTED_LANGUAGES = ["en", "hi", "bn"]


class ContentService:
    """Handles the full AI content pipeline: upload → extract → generate → validate."""

    # -------------------------------------------------------------------------
    # Document ingestion
    # -------------------------------------------------------------------------

    @staticmethod
    async def save_source_document(
        db: AsyncSession,
        *,
        title: str,
        file_bytes: bytes,
        file_type: str,
        uploaded_by: uuid.UUID,
        subject: str = "",
        grade: str = "",
        language: str = "en",
        upload_dir: str = "/tmp/vidyamitra/docs",
    ) -> SourceDocument:
        """Persist uploaded file and queue for extraction."""
        import os
        os.makedirs(upload_dir, exist_ok=True)
        doc_id = uuid.uuid4()
        file_path = os.path.join(upload_dir, f"{doc_id}.{file_type}")
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        doc = SourceDocument(
            id=doc_id,
            title=title,
            file_url=file_path,
            file_type=file_type,
            uploaded_by=uploaded_by,
            subject=subject,
            grade=grade,
            language=language,
            extraction_status="pending",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def extract_text_from_document(
        db: AsyncSession, document_id: uuid.UUID
    ) -> Optional[str]:
        """Extract text from a PDF/document using pypdf (no external API needed)."""
        result = await db.execute(
            select(SourceDocument).where(SourceDocument.id == document_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return None

        await db.execute(
            update(SourceDocument)
            .where(SourceDocument.id == document_id)
            .values(extraction_status="processing")
        )
        await db.commit()

        extracted = ""
        try:
            if doc.file_type == "pdf":
                import pypdf  # type: ignore
                with open(doc.file_url, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    extracted = "\n".join(
                        page.extract_text() or "" for page in reader.pages
                    )
            else:
                # Plain text or markdown
                with open(doc.file_url, "r", errors="ignore") as f:
                    extracted = f.read()

            await db.execute(
                update(SourceDocument)
                .where(SourceDocument.id == document_id)
                .values(extraction_status="completed", extracted_text=extracted)
            )
            await db.commit()
            logger.info(f"Extracted {len(extracted)} chars from document {document_id}")
        except Exception as exc:
            logger.error(f"Extraction failed for {document_id}: {exc}")
            await db.execute(
                update(SourceDocument)
                .where(SourceDocument.id == document_id)
                .values(extraction_status="failed")
            )
            await db.commit()

        return extracted or None

    # -------------------------------------------------------------------------
    # AI lesson generation
    # -------------------------------------------------------------------------

    @staticmethod
    async def generate_lessons_from_document(
        db: AsyncSession,
        document_id: uuid.UUID,
        *,
        tutor_user_ids: list[uuid.UUID],
        grade: str = "3",
        subject: str = "Mathematics",
        curriculum_node_id: Optional[uuid.UUID] = None,
    ) -> list[ContentLesson]:
        """Use AI to generate lessons for all supported languages, then notify tutors."""
        result = await db.execute(
            select(SourceDocument).where(SourceDocument.id == document_id)
        )
        doc = result.scalar_one_or_none()
        if not doc or not doc.extracted_text:
            logger.warning(f"Document {document_id} has no extracted text")
            return []

        lessons_created: list[ContentLesson] = []
        source_snippet = doc.extracted_text[:4000]

        for lang in SUPPORTED_LANGUAGES:
            try:
                lesson_content = await ContentService._ai_generate_lesson(
                    source_snippet=source_snippet,
                    grade=grade,
                    subject=subject,
                    language=lang,
                    document_title=doc.title,
                )

                lesson = ContentLesson(
                    id=uuid.uuid4(),
                    source_document_id=document_id,
                    curriculum_node_id=curriculum_node_id,
                    title=f"{doc.title} — {lang.upper()} (Grade {grade})",
                    content_text=lesson_content,
                    language=lang,
                    status="draft",
                    created_by="ai",
                )
                db.add(lesson)
                lessons_created.append(lesson)
            except Exception as exc:
                logger.error(f"AI lesson generation failed for lang={lang}: {exc}")

        await db.commit()
        for lesson in lessons_created:
            await db.refresh(lesson)

        # Notify each tutor that content is pending their review
        for tutor_user_id in tutor_user_ids:
            for lesson in lessons_created:
                try:
                    await notification_service.create(
                        db,
                        user_id=tutor_user_id,
                        notification_type=NotificationType.CONTENT_PENDING_REVIEW,
                        title="New lesson ready for review",
                        body=f"AI generated '{lesson.title}'. Please review, approve, or modify it before publishing.",
                        priority=NotificationPriority.HIGH,
                        action_url=f"/tutor?tab=reviews&lesson={lesson.id}",
                        entity_id=lesson.id,
                        entity_type="content_lesson",
                    )
                except Exception:
                    pass

        return lessons_created

    @staticmethod
    async def _ai_generate_lesson(
        *,
        source_snippet: str,
        grade: str,
        subject: str,
        language: str,
        document_title: str,
    ) -> str:
        """Call LLM to produce a structured lesson from source material."""
        lang_names = {"en": "English", "hi": "Hindi", "bn": "Bengali"}
        lang_name = lang_names.get(language, "English")

        system_prompt = f"""You are an expert curriculum designer for {subject}, Grade {grade}.
Write a clear, engaging lesson in {lang_name} based on the provided source material.

Structure the lesson with:
1. **Learning Objectives** (2–3 bullet points)
2. **Introduction** (1–2 paragraphs, relatable real-life context)
3. **Core Concepts** (clear explanations with examples)
4. **Worked Examples** (2–3 solved problems, step by step)
5. **Key Takeaways** (3–5 bullet points)

Rules:
- Language: {lang_name} only
- Grade level: {grade} (age-appropriate vocabulary)
- Keep explanations concrete and visual
- Use culturally relevant examples for Indian students
- Do NOT include answers to unsolved practice problems"""

        try:
            response = await model_router.route(
                task_type="curriculum_search",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Source material from '{document_title}':\n\n{source_snippet}\n\nGenerate the lesson now.",
                    },
                ],
                language=language,
            )
            return response.content
        except Exception as exc:
            logger.error(f"LLM lesson generation error: {exc}")
            return f"[Auto-generated lesson for {document_title} — Grade {grade} — {lang_name}]\n\n{source_snippet[:500]}..."

    # -------------------------------------------------------------------------
    # Tutor validation workflow
    # -------------------------------------------------------------------------

    @staticmethod
    async def review_lesson(
        db: AsyncSession,
        *,
        lesson_id: uuid.UUID,
        tutor_id: uuid.UUID,
        tutor_user_id: uuid.UUID,
        action: str,  # "approve" | "reject" | "modify"
        feedback: Optional[str] = None,
        modified_content: Optional[str] = None,
        accuracy_score: Optional[float] = None,
        completeness_score: Optional[float] = None,
        alignment_score: Optional[float] = None,
    ) -> ContentLesson:
        """Record a tutor's review decision and update lesson status."""
        lesson_result = await db.execute(
            select(ContentLesson).where(ContentLesson.id == lesson_id)
        )
        lesson = lesson_result.scalar_one_or_none()
        if not lesson:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Lesson not found")

        if action not in ("approve", "reject", "modify"):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="action must be approve | reject | modify")

        # Persist review record
        review = ContentReview(
            id=uuid.uuid4(),
            lesson_id=lesson_id,
            tutor_id=tutor_id,
            action=action,
            feedback=feedback,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            alignment_score=alignment_score,
        )
        db.add(review)

        # Update lesson state
        now = datetime.now(timezone.utc)
        if action == "approve":
            lesson.status = "published"
            lesson.reviewed_by = tutor_id
            lesson.reviewed_at = now
            lesson.published_at = now
        elif action == "reject":
            lesson.status = "rejected"
            lesson.reviewed_by = tutor_id
            lesson.reviewed_at = now
        elif action == "modify":
            if modified_content:
                lesson.content_text = modified_content
            lesson.status = "published"
            lesson.reviewed_by = tutor_id
            lesson.reviewed_at = now
            lesson.published_at = now

        await db.commit()
        await db.refresh(lesson)
        return lesson

    # -------------------------------------------------------------------------
    # Queries
    # -------------------------------------------------------------------------

    @staticmethod
    async def list_pending_review(
        db: AsyncSession, *, limit: int = 20
    ) -> list[ContentLesson]:
        """Return lessons awaiting tutor review."""
        result = await db.execute(
            select(ContentLesson)
            .where(ContentLesson.status == "draft")
            .order_by(ContentLesson.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_published(
        db: AsyncSession,
        *,
        grade: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50,
    ) -> list[ContentLesson]:
        """Return published lessons, optionally filtered."""
        query = select(ContentLesson).where(ContentLesson.status == "published")
        if grade:
            # Filter via source_document join — simple title contains heuristic
            pass
        if language:
            query = query.where(ContentLesson.language == language)
        query = query.order_by(ContentLesson.published_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())


content_service = ContentService()
