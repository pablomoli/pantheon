"""Muse — ElevenLabs TTS + STT wrapper.

Public API consumed by the gateway (Gabriel's domain):
    transcribe(audio_bytes, mime_type) -> str
    speak(text, voice_id) -> bytes  (OGG/Opus for Telegram)
"""

from __future__ import annotations

import logging
import os

from elevenlabs import AsyncElevenLabs

from voice.exceptions import SpeechError, TranscriptionError
from voice.personas import get_voice_id

logger = logging.getLogger(__name__)

_client: AsyncElevenLabs | None = None


def _get_client() -> AsyncElevenLabs:
    """Return (or create) the async ElevenLabs client."""
    global _client
    if _client is None:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY environment variable is not set")
        _client = AsyncElevenLabs(api_key=api_key)
    return _client


async def transcribe(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """Convert speech audio to text using ElevenLabs STT.

    Args:
        audio_bytes: Raw audio data.
        mime_type: MIME type of the audio (default ``audio/ogg`` for Telegram voice).

    Returns:
        The transcribed text.

    Raises:
        TranscriptionError: If transcription fails.
    """
    client = _get_client()

    # Map MIME type to ElevenLabs file format hint.
    format_map: dict[str, str] = {
        "audio/ogg": "ogg",
        "audio/mpeg": "mp3",
        "audio/wav": "wav",
        "audio/webm": "webm",
    }
    file_ext = format_map.get(mime_type, "ogg")
    file_tuple = (f"audio.{file_ext}", audio_bytes)

    try:
        result = await client.speech_to_text.convert(
            model_id="scribe_v1",
            file=file_tuple,
        )
        text: str = result.text
        if not text.strip():
            raise TranscriptionError("ElevenLabs returned empty transcription")
        return text.strip()
    except TranscriptionError:
        raise
    except Exception as exc:
        raise TranscriptionError(f"Transcription failed: {exc}") from exc


async def speak(text: str, voice_id: str | None = None) -> bytes:
    """Convert text to speech using ElevenLabs TTS.

    Args:
        text: The text to synthesise.
        voice_id: ElevenLabs voice ID (defaults to ``ZEUS_VOICE_ID``).

    Returns:
        OGG/Opus audio bytes ready to send as a Telegram voice message.

    Raises:
        SpeechError: If synthesis fails.
    """
    client = _get_client()
    vid = voice_id or get_voice_id()

    try:
        # convert() returns an async generator directly — do NOT await it.
        audio_iter = client.text_to_speech.convert(
            voice_id=vid,
            text=text,
            output_format="opus_48000_32",
            model_id="eleven_multilingual_v2",
        )
        # Collect the streamed chunks into a single bytes object.
        chunks: list[bytes] = []
        async for chunk in audio_iter:
            chunks.append(chunk)
        audio = b"".join(chunks)

        if not audio:
            raise SpeechError("ElevenLabs returned empty audio")
        return audio
    except SpeechError:
        raise
    except Exception as exc:
        raise SpeechError(f"Speech synthesis failed: {exc}") from exc
