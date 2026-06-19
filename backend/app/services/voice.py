"""Voice Service — Speech-to-Text and Text-to-Speech for EN/HI/BN."""

import io
import logging
import re
from typing import Optional

from openai import AsyncOpenAI
from app.config import settings, TTSProvider

logger = logging.getLogger(__name__)


class VoiceService:
    """Handles STT and TTS pipelines for multilingual voice interaction."""

    def __init__(self):
        self._openai_client = None
        self._elevenlabs_api_key = settings.elevenlabs_api_key
        self._azure_key = settings.azure_speech_key
        self._azure_region = settings.azure_speech_region

    @property
    def openai_client(self) -> AsyncOpenAI:
        if not self._openai_client:
            self._openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    # =========================================================================
    # Speech-to-Text (Whisper)
    # =========================================================================

    async def speech_to_text(
        self,
        audio_data: bytes,
        language_hint: Optional[str] = None,
    ) -> dict:
        """
        Transcribe speech to text using OpenAI Whisper.
        Supports English, Hindi, Bengali, and mixed speech.

        Returns: {"text": str, "language_detected": str, "confidence": float, "duration_seconds": float}
        """
        try:
            # Convert bytes to file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"

            # Whisper API call — with language hint for better accuracy
            kwargs = {
                "model": settings.openai_stt_model,
                "file": audio_file,
                "response_format": "verbose_json",
            }

            if language_hint and language_hint in ("en", "hi", "bn"):
                kwargs["language"] = language_hint

            response = await self.openai_client.audio.transcriptions.create(**kwargs)

            text = response.text.strip()
            detected_lang = getattr(response, 'language', language_hint or 'en')

            # Map Whisper language codes
            lang_map = {"english": "en", "hindi": "hi", "bengali": "bn"}
            detected_lang = lang_map.get(detected_lang, detected_lang[:2] if detected_lang else "en")

            # Calculate approximate duration from segments
            segments = getattr(response, 'segments', [])
            duration = 0.0
            if segments:
                last_segment = segments[-1]
                duration = getattr(last_segment, 'end', 0.0)

            return {
                "text": text,
                "language_detected": detected_lang,
                "confidence": 0.95,  # Whisper doesn't expose per-request confidence
                "duration_seconds": round(duration, 1),
            }

        except Exception as e:
            logger.error(f"STT failed: {e}")
            raise

    # =========================================================================
    # Text-to-Speech
    # =========================================================================

    async def text_to_speech(
        self,
        text: str,
        language: str = "en",
        voice_style: str = "natural",
    ) -> bytes:
        """
        Convert text to speech audio.
        Routes to configured TTS provider.
        Returns audio bytes (MP3/WebM).
        """
        # Preprocess math expressions for speech
        text = self._preprocess_math_for_tts(text, language)

        # Route to appropriate provider
        if settings.tts_provider == TTSProvider.ELEVENLABS and self._elevenlabs_api_key:
            return await self._tts_elevenlabs(text, language, voice_style)
        elif settings.tts_provider == TTSProvider.AZURE and self._azure_key:
            return await self._tts_azure(text, language, voice_style)
        elif settings.tts_provider == TTSProvider.OPENAI:
            return await self._tts_openai(text, language, voice_style)
        else:
            # Fallback: try OpenAI TTS
            logger.warning(f"No TTS provider configured. Trying OpenAI fallback.")
            return await self._tts_openai(text, language, voice_style)

    async def _tts_elevenlabs(
        self, text: str, language: str, voice_style: str
    ) -> bytes:
        """TTS via ElevenLabs API."""
        import httpx

        voice_id = settings.get_tts_voice_id(language)
        if not voice_id:
            voice_id = settings.elevenlabs_voice_id_en

        # Map voice styles to ElevenLabs settings
        stability_map = {
            "natural": 0.5,
            "gentle": 0.3,
            "excited": 0.8,
        }
        stability = stability_map.get(voice_style, 0.5)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self._elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": 0.75,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise Exception(f"ElevenLabs TTS failed: {response.status_code} {response.text}")
            return response.content

    async def _tts_azure(self, text: str, language: str, voice_style: str) -> bytes:
        """TTS via Azure Cognitive Services."""
        import httpx

        # Azure TTS voice mapping
        voice_map = {
            "en": "en-US-JennyNeural",
            "hi": "hi-IN-SwaraNeural",
            "bn": "bn-IN-TanishaaNeural",
        }
        voice_name = voice_map.get(language, voice_map["en"])

        # Map voice styles
        style_map = {
            "natural": "friendly",
            "gentle": "gentle",
            "excited": "cheerful",
        }
        style = style_map.get(voice_style, "friendly")

        # SSML for better quality
        ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{language}-IN'>
            <voice name='{voice_name}'>
                <mstts:express-as style='{style}'>
                    {text}
                </mstts:express-as>
            </voice>
        </speak>"""

        url = f"https://{self._azure_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": self._azure_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, content=ssml, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Azure TTS failed: {response.status_code}")
            return response.content

    async def _tts_openai(self, text: str, language: str, voice_style: str) -> bytes:
        """TTS via OpenAI TTS API."""
        # OpenAI TTS voice mapping
        voice_map = {
            "natural": "nova",
            "gentle": "alloy",
            "excited": "shimmer",
        }
        voice = voice_map.get(voice_style, "nova")

        try:
            response = await self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3",
            )
            return response.content
        except Exception as e:
            logger.error(f"OpenAI TTS failed: {e}")
            raise

    # =========================================================================
    # Math Preprocessing for TTS
    # =========================================================================

    def _preprocess_math_for_tts(self, text: str, language: str) -> str:
        """
        Convert math expressions to speakable text.
        Handles LaTeX, inline math, and common math patterns.
        """
        # Remove LaTeX delimiters but keep content for processing
        text = re.sub(r'\$\$([^$]+)\$\$', r'\1', text)
        text = re.sub(r'\$([^$]+)\$', r'\1', text)

        # Age-appropriate math→speech patterns
        speech_patterns = {
            # Superscripts (squared, cubed, etc.)
            r'(\w+)\^2': self._math_speech(r'\1 squared', language, r'\1 वर्ग', r'\1 বর্গ'),
            r'(\w+)\^3': self._math_speech(r'\1 cubed', language, r'\1 घन', r'\1 ঘন'),
            r'(\w+)\^(\d+)': self._math_speech(r'\1 to the power \2', language, r'\1 की घात \2', r'\1 এর ঘাত \2'),

            # Operators
            r'\\times': self._math_speech('times', language, 'गुणा', 'গুণ'),
            r'\\div': self._math_speech('divided by', language, 'भागा', 'ভাগ'),
            r'\\sqrt\{([^}]+)\}': self._math_speech(r'square root of \1', language, r'\1 का वर्गमूल', r'\1 এর বর্গমূল'),
            r'\\frac\{([^}]+)\}\{([^}]+)\}': self._math_speech(r'\1 over \2', language, r'\1 बटा \2', r'\1 ভাগ \2'),

            # Common expressions
            r'\\pi': 'pi',
            r'\\infty': self._math_speech('infinity', language, 'अनंत', 'অসীম'),
            r'\\sum': self._math_speech('sum of', language, 'का योग', 'এর যোগফল'),

            # Simple operators
            r'\*': self._math_speech(' times ', language, ' गुणा ', ' গুণ '),
            r'/': self._math_speech(' divided by ', language, ' भागा ', ' ভাগ '),
            r'\+': self._math_speech(' plus ', language, ' जोड़ ', ' যোগ '),
            r'=': self._math_speech(' equals ', language, ' बराबर ', ' সমান '),
        }

        # Grade-appropriate processing
        for pattern, replacement in speech_patterns.items():
            text = re.sub(pattern, replacement, text)

        return text.strip()

    def _math_speech(self, en: str, lang: str, hi: str, bn: str) -> str:
        """Get math speech in the appropriate language."""
        if lang == "hi":
            return hi
        elif lang == "bn":
            return bn
        return en


# Singleton
voice_service = VoiceService()
