"""Voice API endpoints: STT, TTS."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/stt")
async def speech_to_text():
    pass  # Phase 2


@router.post("/tts")
async def text_to_speech():
    pass  # Phase 2
