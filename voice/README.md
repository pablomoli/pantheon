# Voice Module (Muse)

This folder provides speech-to-text (STT) and text-to-speech (TTS) capabilities used by Pantheon voice interactions.

## Responsibilities

- Transcribe incoming audio (primary: ElevenLabs, fallback: Gemini)
- Generate spoken responses from text using selected personas/voice IDs
- Provide typed exceptions for voice pipeline failures

## Files

- `client.py`: async STT/TTS client functions
- `personas.py`: voice/persona constants and mappings
- `exceptions.py`: voice-domain exception types

## Public Interface

`client.py` provides:

- `transcribe(audio_bytes, mime_type="audio/ogg") -> str`
- `speak(text, voice_id=None) -> bytes`

Both are async and designed for gateway/agent integration.

## Required Environment Variables

- `ELEVENLABS_API_KEY` (preferred) or `ELEVENLABS_API`
- `GEMINI_API` (fallback transcription)

## Usage Example

```python
from voice.client import speak, transcribe

text = await transcribe(audio_payload, mime_type="audio/ogg")
reply_audio = await speak("Copy. Analysis complete.")
```

## Development Notes

- Keep all outbound HTTP calls async (`httpx.AsyncClient`).
- Avoid logging raw audio bytes or sensitive user content.
- Ensure exceptions preserve actionable error context for gateway handlers.
