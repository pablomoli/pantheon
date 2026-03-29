# Voice Module (Muse)

This folder provides the full voice interaction layer for Pantheon: speech-to-text, text-to-speech, ElevenLabs Conversational AI agent bridging, and sandbox-connected tool implementations.

## Responsibilities

- Transcribe incoming audio (primary: ElevenLabs, fallback: Gemini)
- Generate spoken responses from text using selected personas/voice IDs
- Bridge text conversations to/from the ElevenLabs Conversational AI WebSocket agent
- Expose client tools (analyze, report, status) so the voice agent can trigger sandbox operations during live calls

## Files

| File | Description |
| --- | --- |
| `client.py` | Async STT/TTS client — `transcribe()` and `speak()` |
| `agent.py` | ElevenLabs Conversational AI agent bridge — opens WebSocket session, sends text, returns response |
| `tools.py` | Voice agent tool implementations — `tool_analyze`, `tool_report`, `tool_status` — connects Muse to sandbox |
| `personas.py` | Voice/persona constants and mappings |
| `exceptions.py` | Voice-domain exception types |
| `__init__.py` | Package exports |

## Public Interface

### `client.py`

- `transcribe(audio_bytes, mime_type="audio/ogg") -> str` — STT via ElevenLabs or Gemini fallback
- `speak(text, voice_id=None) -> bytes` — TTS audio generation

### `agent.py`

- `ask_agent(text) -> str` — send text to ElevenLabs agent, return full response

### `tools.py` (ElevenLabs ClientTools)

Registered on the ElevenLabs Conversational AI agent as client-side tools:

- `tool_analyze(parameters)` — submit sample to sandbox, poll until report is ready (up to 90s)
- `tool_report(parameters)` — retrieve analysis report for a given job ID
- `tool_status(parameters)` — check sandbox health

These tools enable Muse to trigger and report on malware analysis during live voice calls without the conversation disconnecting.

## Required Environment Variables

| Variable | Description |
| --- | --- |
| `ELEVENLABS_API_KEY` | ElevenLabs API key (or `ELEVENLABS_API` as alias) |
| `ELEVENLABS_AGENT_ID` | ElevenLabs Conversational AI agent ID |
| `GEMINI_API` | Gemini API key (fallback transcription) |
| `SANDBOX_API_URL` | Hephaestus service URL (default: `http://localhost:9000`) |

## Usage Example

```python
from voice.client import speak, transcribe
from voice.agent import ask_agent

# STT → LLM → TTS
text = await transcribe(audio_payload, mime_type="audio/ogg")
response = await ask_agent(text)
reply_audio = await speak(response)
```

## Development Notes

- Keep all outbound HTTP calls async (`httpx.AsyncClient`).
- `from __future__ import annotations` at the top of every file.
- Avoid logging raw audio bytes or sensitive user content.
- Ensure exceptions preserve actionable error context for gateway handlers.
- The `tool_analyze` implementation includes an ADK fallback path — if the sandbox is unreachable, it routes through the `gateway.runner` agent pipeline instead.
