from __future__ import annotations

import pytest
from sandbox.models import (
    AgentName,
    AttackStage,
    DetonationResult,
    EventType,
    NetworkEvent,
    PantheonEvent,
    ProcessEvent,
)


def test_pantheon_event_defaults_id_and_ts() -> None:
    event = PantheonEvent(type=EventType.AGENT_ACTIVATED)
    assert len(event.id) == 36  # uuid4
    assert "T" in event.ts      # ISO 8601


def test_pantheon_event_serializes_to_json() -> None:
    event = PantheonEvent(
        type=EventType.TOOL_CALLED,
        agent=AgentName.HADES,
        tool="submit_sample",
        job_id="abc123",
        payload={"file_path": "/tmp/sample.js"},
    )
    data = event.model_dump(mode="json")
    assert data["type"] == "tool_called"
    assert data["agent"] == "hades"
    assert data["payload"]["file_path"] == "/tmp/sample.js"


def test_process_event_fields() -> None:
    ev = ProcessEvent(
        event_type="file_write",
        path="C:\\Users\\Public\\Mands.png",
        process="wscript.exe",
        pid=1234,
    )
    assert ev.event_type == "file_write"
    assert ev.value is None


def test_network_event_fields() -> None:
    ev = NetworkEvent(
        event_type="dns_query",
        host="evil.example.com",
    )
    assert ev.path is None


def test_detonation_result_defaults_empty() -> None:
    result = DetonationResult()
    assert result.process_events == []
    assert result.network_events == []
    assert result.error is None


def test_attack_stage_fields() -> None:
    stage = AttackStage(
        stage_id="persistence",
        label="Registry Persistence",
        description="Writes HKCU Run key",
        icon="persistence",
    )
    assert stage.stage_id == "persistence"
