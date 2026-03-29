# Test Suite

This folder contains integration and module-level tests for the Pantheon backend stack.

## Structure

- `conftest.py`: shared pytest fixtures and test configuration
- `agents/`: tests for orchestration, tools, and agent behavior
- `sandbox/`: tests for API routes, analyzer behavior, and event flow

Agent-local tests may also exist in module folders (for example under `agents/tests/`).

## Run Tests

From repository root:

```bash
uv sync
uv run pytest
```

Target specific suites:

```bash
uv run pytest tests/agents
uv run pytest tests/sandbox
uv run pytest agents/tests
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
