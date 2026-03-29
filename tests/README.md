# Test Suite

This folder contains integration and module-level tests for the Pantheon backend stack.

## Structure

### Top-Level Test Files

| File | Scope |
| --- | --- |
| `conftest.py` | shared pytest fixtures and test configuration |
| `test_bot.py` | Hermes Telegram bot — message handling, file uploads, command routing |
| `test_runner.py` | ADK runner bridge — agent dispatch and session management |
| `test_session.py` | session manager — user_id → session_id mapping |
| `test_voice.py` | Muse voice module — STT, TTS, agent bridge, client tools |
| `test_webapp.py` | voice call Mini App — FastAPI endpoints, webhooks |

### Subdirectories

- `agents/`: tests for orchestration, tools, and agent behavior
- `sandbox/`: tests for API routes, analyzer behavior, and event flow

Agent-local tests may also exist in `agents/tests/`.

## Run Tests

From repository root:

```bash
uv sync
uv run pytest
```

Target specific suites:

```bash
uv run pytest tests/                 # all top-level tests
uv run pytest tests/agents           # agent tests
uv run pytest tests/sandbox          # sandbox tests
uv run pytest agents/tests           # agent-local tests
uv run pytest tests/test_voice.py    # voice module only
uv run pytest tests/test_bot.py      # telegram bot only
```

## Quality Gates

Use these together before merge:

```bash
uv run mypy .
uv run ruff check .
uv run pytest
```

## Testing Guidelines

- Keep tests deterministic and avoid external network dependence.
- Prefer fixtures/fakes over live integrations for unit-level coverage.
- Validate safety-critical behavior (malware handling boundaries, event emission, API contracts).
- Use `pytest-asyncio` for async tests (configured as `asyncio_mode = "auto"` in pyproject.toml).
