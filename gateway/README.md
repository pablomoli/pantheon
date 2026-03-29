# Gateway (Hermes)

Hermes is the Telegram gateway and voice call interface for Pantheon. It is the primary user-facing entry point — operators interact with the system through text, voice messages, file uploads, and real-time voice calls.

## Responsibilities

- Receive and route Telegram messages (text, voice, video, file uploads)
- Bridge user input to the ADK agent pipeline (Zeus → Athena → Hades → Apollo → Ares)
- Provide ElevenLabs Conversational AI voice call interface via Telegram Mini App
- Transcribe voice messages (via Muse STT) and synthesize voice responses (via Muse TTS)
- Emit dashboard telemetry events for Hermes activation and Zeus handoffs

## Files

| File | Description |
| --- | --- |
| `bot.py` | Telegram bot — command handlers (/start, /reset, /status, /call), message handlers (text, voice, video, document), typing indicators, and event emission |
| `webapp.py` | FastAPI Mini App server — serves `call.html` voice call interface, agent config API, and tool webhooks for ElevenLabs |
| `runner.py` | ADK runner bridge — routes messages to Zeus (ADK pipeline) with ElevenLabs fallback for conversational queries |
| `session.py` | ADK session manager — maps `user_id → session_id` via `InMemorySessionService` |
| `static/call.html` | Voice call Mini App — browser-based ElevenLabs WebSocket interface with client tools (analyze, report, status) |

## Message Flow

```
User → Telegram → bot.py
  ├── text message → runner.py → Zeus (ADK)
  ├── voice message → Muse STT → runner.py → Zeus (ADK) → Muse TTS → voice reply
  ├── file upload → save to SAMPLES_DIR → runner.py → Zeus (ADK, forced) → analysis
  └── /call command → Mini App (call.html) → ElevenLabs WebSocket → client tools → sandbox
```

## Bot Commands

| Command | Description |
| --- | --- |
| `/start` | Welcome message and usage instructions |
| `/call` | Open the voice call Mini App in Telegram |
| `/reset` | Clear the user's ADK session |
| `/status` | Check if an analysis is currently running |

## Runner Priority

The `runner.py` module routes messages through:

1. **ADK pipeline** (Zeus → full swarm) — always preferred, emits dashboard events
2. **ElevenLabs Conversational AI** — fallback only for non-analysis conversational queries

Analysis prompts (file uploads, `force_adk=True`, or explicit analyze phrases) **never** fall through to ElevenLabs.

## Required Environment Variables

| Variable | Description |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (or `TELEGRAM_API` as alias) |
| `ELEVENLABS_API_KEY` | ElevenLabs API key (for voice I/O) |
| `ELEVENLABS_AGENT_ID` | ElevenLabs agent ID (for /call Mini App) |
| `WEBAPP_BASE_URL` | Public HTTPS base URL for Mini App + webhooks |
| `WEBAPP_PORT` | Port for the FastAPI Mini App server (default: 8443) |
| `SANDBOX_API_URL` | Hephaestus service URL (for event emission) |
| `SAMPLES_DIR` | Directory for uploaded sample files (default: `/tmp/samples`) |

## Local Development

From repository root:

```bash
uv sync
uv run python run.py    # starts bot + webapp + sandbox together
```

## Testing

```bash
uv run pytest tests/test_bot.py tests/test_runner.py tests/test_session.py tests/test_webapp.py
```

## Design Notes

- Never expose sandbox API or raw IOC data directly to the user — all interaction flows through agents.
- Never commit bot tokens or API keys.
- Use `python-telegram-bot`'s async API throughout.
- Event emission is fire-and-forget — never let telemetry block user-facing responses.
- `from __future__ import annotations` at the top of every file.
