"""Tests for voice module — ElevenLabs TTS + STT via httpx."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from voice import client as voice_client
from voice.exceptions import SpeechError, TranscriptionError


# ---------------------------------------------------------------------------
# transcribe()
# ---------------------------------------------------------------------------


async def test_transcribe_empty_payload_raises() -> None:
    with pytest.raises(TranscriptionError, match="Empty audio"):
        await voice_client.transcribe(b"")


@patch.dict("os.environ", {"ELEVENLABS_API_KEY": "fake-key"})
async def test_transcribe_returns_text() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"text": "hello world"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("voice.client.httpx.AsyncClient", return_value=mock_client):
        text = await voice_client.transcribe(b"fake-audio", "audio/ogg")
    assert text == "hello world"


@patch.dict("os.environ", {"ELEVENLABS_API_KEY": "fake-key"})
async def test_transcribe_empty_text_falls_back_to_gemini() -> None:
    """When ElevenLabs returns empty text, Gemini fallback is tried."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"text": ""}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("voice.client.httpx.AsyncClient", return_value=mock_client):
        with patch(
            "voice.client._transcribe_gemini",
            AsyncMock(return_value="gemini result"),
        ):
            text = await voice_client.transcribe(b"fake-audio")
    assert text == "gemini result"


@patch.dict("os.environ", {"ELEVENLABS_API_KEY": "fake-key"})
async def test_transcribe_both_fail_raises() -> None:
    """When both ElevenLabs and Gemini fail, TranscriptionError is raised."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=RuntimeError("API down"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("voice.client.httpx.AsyncClient", return_value=mock_client):
        with patch(
            "voice.client._transcribe_gemini",
            AsyncMock(side_effect=RuntimeError("Gemini down")),
        ):
            with pytest.raises(TranscriptionError, match="Transcription failed"):
                await voice_client.transcribe(b"fake-audio")


# ---------------------------------------------------------------------------
# speak()
# ---------------------------------------------------------------------------


async def test_speak_empty_text_raises() -> None:
    with pytest.raises(SpeechError, match="non-empty"):
        await voice_client.speak("   ")


@patch.dict("os.environ", {"ELEVENLABS_API_KEY": "fake-key"})
async def test_speak_returns_audio_bytes() -> None:
    mock_response = MagicMock()
    mock_response.content = b"audio-data"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("voice.client.httpx.AsyncClient", return_value=mock_client):
        audio = await voice_client.speak("hello")
    assert audio == b"audio-data"


@patch.dict("os.environ", {"ELEVENLABS_API_KEY": "fake-key"})
async def test_speak_empty_audio_raises() -> None:
    mock_response = MagicMock()
    mock_response.content = b""
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("voice.client.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(SpeechError, match="empty"):
            await voice_client.speak("hello")


@patch.dict("os.environ", {"ELEVENLABS_API_KEY": "fake-key"})
async def test_speak_http_error_raises() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "500", request=MagicMock(), response=MagicMock()
        )
    )

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("voice.client.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(SpeechError, match="ElevenLabs TTS failed"):
            await voice_client.speak("hello")


# ---------------------------------------------------------------------------
# _get_elevenlabs_api_key()
# ---------------------------------------------------------------------------


def test_missing_api_key_raises() -> None:
    with patch.dict("os.environ", {}, clear=True):
        import os

        os.environ.pop("ELEVENLABS_API_KEY", None)
        os.environ.pop("ELEVENLABS_API", None)
        with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
            voice_client._get_elevenlabs_api_key()
