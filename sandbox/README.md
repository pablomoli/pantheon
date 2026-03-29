# Sandbox (Hephaestus)

Hephaestus is the FastAPI service that powers malware analysis, persistence, and event streaming.

## Responsibilities

- Accept sample submissions for analysis
- Run static and optional dynamic pipelines via `Analyzer`
- Persist reports/IOCs and agent memory in SQLite
- Expose similarity/fingerprint APIs
- Broadcast real-time events to dashboard clients over WebSocket

## Key Files

- `main.py`: FastAPI app, endpoints, and service lifecycle
- `analyzer.py`: analysis orchestration + persistence logic
- `models.py`: Pydantic API contract (single source of truth)
- `events.py`: in-memory EventBus used by `/ws` and `/events`
- `static/`: static analysis components and extraction logic
- `dynamic/`: containerized dynamic analysis harness

## API Endpoints

- `GET /sandbox/health`
- `POST /sandbox/analyze`
- `GET /sandbox/report/{job_id}`
- `GET /sandbox/iocs/{job_id}`
- `POST /sandbox/memory`
- `GET /sandbox/memory/{job_id}/{agent_name}`
- `POST /sandbox/fingerprint/{job_id}`
- `GET /sandbox/similar/{job_id}`
- `POST /events` (event ingest)
- `GET /ws` (event stream)

## Event System

`events.py` exposes a module-level bus singleton.

- Producers post `PantheonEvent` payloads to `POST /events`.
- Dashboard clients subscribe to `GET /ws`.
- Events are broadcast fan-out style to all connected subscribers.

## Running Locally

From repository root:

```bash
uv sync
uv run python run.py
```

Service default address: `http://localhost:9000`

## Quality Checks

```bash
uv run mypy sandbox
uv run ruff check sandbox
uv run pytest tests/sandbox
```

## Safety Constraints

- Dynamic execution must stay inside approved isolation boundaries.
- Never run malware directly in this process or host shell.
- Keep `models.py` stable and coordinate contract changes across teams.
