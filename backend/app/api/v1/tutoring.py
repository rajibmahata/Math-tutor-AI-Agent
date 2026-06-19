"""Tutoring API + WebSocket handler — full implementation."""

import json
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_student
from app.models.user import User
from app.models.student import Student
from app.services.tutoring import TutoringService
from app.services.student import StudentService
from app.schemas.common import StartSessionRequest

logger = logging.getLogger(__name__)

router = APIRouter()

# Active WebSocket connections: {session_id: WebSocket}
_active_connections: dict[str, WebSocket] = {}


@router.post("/sessions")
async def start_session(
    body: StartSessionRequest,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Start a new tutoring session. Returns session with WS endpoint."""
    service = TutoringService(db)
    try:
        session = await service.start_session(
            student_id=student.id,
            session_type=body.session_type,
            language=body.language,
            topic_id=body.topic_id,
        )
        await db.commit()

        ws_endpoint = f"ws://localhost:8000/api/v1/ws/sessions/{session.id}?token=demo"

        return {
            "id": str(session.id),
            "student_id": str(session.student_id),
            "session_type": session.session_type,
            "language": session.language,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
            "ws_endpoint": ws_endpoint,
        }
    except Exception:
        await db.rollback()
        raise


@router.get("/sessions")
async def list_sessions(
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
    status: str = Query(default=None),
    limit: int = Query(default=20, le=50),
):
    """List sessions for the current student."""
    from sqlalchemy import select
    from app.models.session import Session

    query = select(Session).where(Session.student_id == student.id)
    if status:
        query = query.where(Session.status == status)

    query = query.order_by(Session.started_at.desc()).limit(limit)
    result = await db.execute(query)
    sessions = result.scalars().all()

    return {
        "data": [
            {
                "id": str(s.id),
                "session_type": s.session_type,
                "language": s.language,
                "questions_asked": s.questions_asked,
                "questions_correct": s.questions_correct,
                "duration_seconds": s.duration_seconds,
                "status": s.status,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            }
            for s in sessions
        ],
        "pagination": {"next_cursor": None, "has_more": len(sessions) == limit},
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get a session by ID."""
    from sqlalchemy import select
    from app.models.session import Session

    result = await db.execute(
        select(Session).where(
            (Session.id == UUID(session_id)) & (Session.student_id == student.id)
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Session", session_id)

    return {
        "id": str(session.id),
        "session_type": session.session_type,
        "language": session.language,
        "questions_asked": session.questions_asked,
        "questions_correct": session.questions_correct,
        "hints_used": session.hints_used,
        "duration_seconds": session.duration_seconds,
        "status": session.status,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
    }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, le=100),
):
    """Get messages for a session."""
    service = TutoringService(db)
    messages = await service.get_session_messages(UUID(session_id), limit=limit)

    return {
        "data": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "content_type": m.content_type,
                "hint_level": m.hint_level,
                "is_correct": m.is_correct,
                "math_expression": m.math_expression,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
        "pagination": {"next_cursor": None, "has_more": len(messages) == limit},
    }


# =========================================================================
# WebSocket Handler — Real-time Tutoring
# =========================================================================

@router.websocket("/ws/sessions/{session_id}")
async def websocket_session(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket endpoint for real-time tutoring interaction."""
    await websocket.accept()
    _active_connections[session_id] = websocket

    # Create a DB session
    from app.core.database import async_session as async_session_factory
    from sqlalchemy import select

    try:
        async with async_session_factory() as db:
            tutoring = TutoringService(db)
            student_svc = StudentService(db)

            # Load session
            result = await db.execute(
                select(Session).where(Session.id == UUID(session_id))
            )
            session = result.scalar_one_or_none()

            if not session:
                await websocket.send_json({
                    "type": "error",
                    "code": "SESSION_NOT_FOUND",
                    "message": "Session not found",
                })
                await websocket.close()
                return

            # Load student
            student = await student_svc.get_profile(session.student_id)
            if not student:
                await websocket.send_json({
                    "type": "error",
                    "code": "STUDENT_NOT_FOUND",
                    "message": "Student profile not found",
                })
                await websocket.close()
                return

            # Send welcome message
            greetings = {
                "en": f"Hi! I'm your math tutor. What would you like to learn today? 😊",
                "hi": f"नमस्ते! मैं आपका गणित टीचर हूँ। आज क्या सीखना चाहोगे? 😊",
                "bn": f"নমস্কার! আমি তোমার গণিত শিক্ষক। আজ কী শিখতে চাও? 😊",
            }
            lang = session.language or "en"
            await websocket.send_json({
                "type": "text",
                "content": greetings.get(lang, greetings["en"]),
                "timestamp": None,
            })

            # Save system welcome
            await tutoring.save_message(
                session_id=UUID(session_id),
                role="teacher",
                content=greetings.get(lang, greetings["en"]),
                content_type="text",
            )

            # Main message loop
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "message")

                if msg_type == "message":
                    # Student sends a question or answer
                    content = data.get("content", "")

                    # Save student message
                    await tutoring.save_message(
                        session_id=UUID(session_id),
                        role="student",
                        content=content,
                        content_type="text",
                    )

                    # Determine if this is an answer to a previous question
                    # Simple heuristic: if the content is short and looks like a number/answer
                    is_potential_answer = _looks_like_answer(content)

                    if is_potential_answer:
                        response_data = await tutoring.process_student_answer(
                            session_id=UUID(session_id),
                            student_answer=content,
                            student=student,
                            language=lang,
                        )
                    else:
                        response_data = await tutoring.process_student_message(
                            session_id=UUID(session_id),
                            student_message=content,
                            student=student,
                            language=lang,
                        )

                    response_data["timestamp"] = None
                    await websocket.send_json(response_data)
                    await db.commit()

                elif msg_type == "hint_request":
                    # Student requests a hint
                    hint_level = data.get("hint_level", 1)
                    response_data = await tutoring.generate_hint(
                        session_id=UUID(session_id),
                        hint_level=hint_level,
                        student=student,
                        language=lang,
                    )
                    # Save hint
                    await tutoring.save_message(
                        session_id=UUID(session_id),
                        role="teacher",
                        content=response_data["content"],
                        content_type="hint",
                        hint_level=hint_level,
                    )
                    response_data["timestamp"] = None
                    await websocket.send_json(response_data)
                    await db.commit()

                elif msg_type == "solution_request":
                    # Student requests full solution
                    response_data = await tutoring.generate_solution(
                        session_id=UUID(session_id),
                        student=student,
                        language=lang,
                    )
                    # Format steps as content
                    steps_text = "\n\n".join(
                        f"**Step {s['step']}:** {s['text']}"
                        for s in response_data.get("steps", [])
                    )
                    await tutoring.save_message(
                        session_id=UUID(session_id),
                        role="teacher",
                        content=steps_text,
                        content_type="solution",
                    )
                    response_data["timestamp"] = None
                    await websocket.send_json(response_data)
                    await db.commit()

                elif msg_type == "language_change":
                    new_lang = data.get("language", "en")
                    if new_lang in ("en", "hi", "bn"):
                        lang = new_lang
                        session.language = new_lang
                        await websocket.send_json({
                            "type": "system",
                            "content": f"Language changed to {new_lang}",
                            "timestamp": None,
                        })
                        await db.commit()

                elif msg_type == "end_session":
                    await tutoring.end_session(UUID(session_id))
                    await db.commit()

                    # Send session summary
                    session_data = {
                        "type": "session_summary",
                        "data": {
                            "questions_asked": session.questions_asked,
                            "questions_correct": session.questions_correct,
                            "hints_used": session.hints_used,
                            "duration_seconds": session.duration_seconds,
                            "points_earned": 0,
                        },
                        "timestamp": None,
                    }
                    await websocket.send_json(session_data)
                    await websocket.close()
                    break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session {session_id}")
        # Auto-save on disconnect
        try:
            async with async_session_factory() as db:
                tutoring = TutoringService(db)
                await tutoring.end_session(UUID(session_id))
                await db.commit()
        except Exception:
            pass

    finally:
        _active_connections.pop(session_id, None)


def _looks_like_answer(content: str) -> bool:
    """Heuristic: does this message look like a math answer (not a question)?"""
    content = content.strip()

    # Short numeric answers
    if len(content) <= 10 and any(c.isdigit() for c in content):
        return True

    # Single word/number after a question was asked
    if len(content.split()) == 1:
        return True

    # Starts with a number or equals sign
    if content[0].isdigit() or content.startswith("="):
        return True

    return False


# Import at module level
from app.models.session import Session
"""Tutoring Chat API — single-shot chat endpoint for frontend"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_student
from app.models.student import Student
from app.services.student import StudentService

# router already defined above


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    language: str = "en"
    action: str = "hint"    # "hint" | "evaluate" | "greeting" | "solution"
    hint_level: int = 1
    question: str | None = None  # Original question context for evaluate/solution


async def _get_student_name(student: Student, db: AsyncSession) -> str:
    """Get student's full name from User table."""
    from sqlalchemy import select
    from app.models.user import User
    result = await db.execute(select(User.full_name).where(User.id == student.user_id))
    name = result.scalar_one_or_none()
    return name or ""


def student_name_from_db(student: Student, db: AsyncSession) -> str:
    """Sync wrapper for name lookup."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return ""  # Can't run sync in async context
        return loop.run_until_complete(_get_student_name(student, db))
    except RuntimeError:
        return ""


@router.post("/chat")
async def chat_endpoint(
    body: ChatRequest,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Handle a chat message from the student — returns AI response."""
    tutoring = TutoringService(db)

    # Auto-create session if none provided
    session_id = None
    if body.session_id:
        try:
            session_id = UUID(body.session_id)
        except ValueError:
            pass

    if not session_id:
        session = await tutoring.start_session(
            student_id=student.id,
            session_type="tutoring",
            language=body.language,
        )
        await db.commit()
        session_id = session.id
    else:
        session_id = UUID(body.session_id)

    # Save student message (always — needed for context)
    await tutoring.save_message(
        session_id=session_id,
        role="student",
        content=body.message,
        content_type="text",
    )

    try:
        if body.action == "greeting":
            from app.agents.orchestrator import orchestrator, AgentContext
            student_name = (await _get_student_name(student, db)) or ""
            ctx = AgentContext(
                student_id=str(student.id),
                student_name=student_name,
                grade=student.grade,
                language=body.language,
                session_id=str(session_id),
                message=body.message,
                streak=student.current_streak,
                points=student.total_points,
                accuracy_rate=student.accuracy_rate,
            )
            ctx = await orchestrator.process(ctx)
            response_data = {"content": ctx.response, "type": "greeting"}
        elif body.action == "hint":
            from app.agents.orchestrator import orchestrator, AgentContext
            ctx = AgentContext(
                student_id=str(student.id),
                student_name=(await _get_student_name(student, db)),
                grade=student.grade,
                language=body.language,
                last_question=body.message,
                hint_level=body.hint_level,
            )
            hint_text = await orchestrator.generate_hint(ctx, body.hint_level)
            response_data = {"content": hint_text, "type": "hint", "hint_level": body.hint_level}
            await tutoring.save_message(
                session_id=session_id,
                role="teacher",
                content=hint_text,
                content_type="hint",
                hint_level=body.hint_level,
            )
        elif body.action == "evaluate":
            from app.agents.orchestrator import orchestrator, AgentContext
            # Use provided question, or find from session messages
            last_question = body.question or body.message
            if not body.question:
                recent = await tutoring.get_session_messages(session_id, limit=20)
                passed_answer = False
                for m in reversed(recent):
                    if not passed_answer and m.role == "student" and m.content.strip() == body.message.strip():
                        passed_answer = True
                        continue
                    if passed_answer and m.role == "student":
                        last_question = m.content
                        break
            
            student_name = (await _get_student_name(student, db)) or ""
            ctx = AgentContext(
                student_id=str(student.id),
                student_name=student_name,
                grade=student.grade,
                language=body.language,
                last_question=last_question,
                student_answer=body.message,
            )
            ctx = await orchestrator._run_assessment_flow(ctx)
            response_data = {"content": ctx.response, "type": "feedback"}
            
            # Update student twin
            await tutoring._update_student_twin(student, {"is_correct": ctx.is_correct})
        elif body.action == "solution":
            from app.agents.orchestrator import orchestrator, AgentContext
            recent = await tutoring.get_session_messages(session_id, limit=15)
            last_question = body.message
            for m in reversed(recent):
                if m.role == "student" and m.content.strip() != body.message.strip():
                    if any(c.isdigit() for c in m.content):
                        last_question = m.content
                        break
            
            student_name = (await _get_student_name(student, db)) or ""
            ctx = AgentContext(
                student_id=str(student.id),
                student_name=student_name,
                grade=student.grade,
                language=body.language,
                last_question=last_question,
            )
            steps_text = await orchestrator.generate_solution(ctx)
            response_data = {"content": steps_text, "type": "solution"}
            await tutoring.save_message(
                session_id=session_id,
                role="teacher",
                content=steps_text,
                content_type="solution",
            )
        else:
            response_data = await tutoring.process_student_message(
                session_id=session_id,
                student_message=body.message,
                student=student,
                language=body.language,
            )

        await db.commit()
        return {
            "content": response_data.get("content", ""),
            "type": response_data.get("type", "text"),
            "hint_level": response_data.get("hint_level"),
            "session_id": str(session_id),
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
