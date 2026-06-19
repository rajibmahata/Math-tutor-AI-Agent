"""Voice API endpoints — STT and TTS."""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.voice import voice_service
from app.schemas.common import TTSRequest

router = APIRouter()


@router.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form(default=None),
):
    """Transcribe speech to text. Supports EN/HI/BN."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio format (webm, mp3, wav, m4a)",
        )

    audio_data = await audio.read()

    if len(audio_data) > 10 * 1024 * 1024:  # 10MB limit
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file too large (max 10MB)",
        )

    result = await voice_service.speech_to_text(
        audio_data=audio_data,
        language_hint=language,
    )

    return result


@router.post("/tts")
async def text_to_speech(
    body: TTSRequest,
):
    """Convert text to speech audio. Returns audio/mpeg."""
    try:
        audio_bytes = await voice_service.text_to_speech(
            text=body.text,
            language=body.language,
            voice_style=body.voice_style,
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "public, max-age=300",
            },
        )
    except Exception as e:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"TTS service unavailable: {str(e)}",
        )
