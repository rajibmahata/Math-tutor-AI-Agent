"""Tutoring API endpoints: session management, WebSocket handler."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/sessions")
async def start_session():
    pass  # Phase 1


@router.get("/sessions")
async def list_sessions():
    pass  # Phase 1


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    pass  # Phase 1


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    pass  # Phase 1


@router.websocket("/ws/sessions/{session_id}")
async def websocket_session(websocket, session_id: str):
    pass  # Phase 1
