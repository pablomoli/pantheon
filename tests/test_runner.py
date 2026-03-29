"""Tests for gateway.runner — ADK runner bridge."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gateway import runner as runner_mod


@pytest.fixture(autouse=True)
def _reset_runner() -> None:
    """Clear the cached runner between tests."""
    runner_mod._runner = None


def _make_event(text: str) -> MagicMock:
    """Create a minimal mock Event with a single text Part."""
    event = MagicMock()
    part = MagicMock()
    part.text = text
    event.content = MagicMock()
    event.content.parts = [part]
    return event


def _make_empty_event() -> MagicMock:
    """Event whose content has no parts."""
    event = MagicMock()
    event.content = MagicMock()
    event.content.parts = []
    return event


async def _async_gen(*events: MagicMock) -> AsyncGenerator[MagicMock, None]:
    for e in events:
        yield e


@patch("gateway.runner._get_runner")
@patch("gateway.runner.create_or_get_session")
async def test_get_agent_response_concatenates_parts(
    mock_session: AsyncMock,
    mock_get_runner: MagicMock,
) -> None:
    session = MagicMock()
    session.id = "sess_1"
    mock_session.return_value = session

    mock_runner = MagicMock()
    mock_runner.run_async = MagicMock(
        return_value=_async_gen(_make_event("Hello "), _make_event("world!")),
    )
    mock_get_runner.return_value = mock_runner

    result = await runner_mod.get_agent_response("u1", "hi")
    assert result == "Hello world!"


@patch("gateway.runner._has_elevenlabs_agent", return_value=False)
@patch("gateway.runner._get_runner")
@patch("gateway.runner.create_or_get_session")
async def test_empty_response_returns_fallback(
    mock_session: AsyncMock,
    mock_get_runner: MagicMock,
    _mock_has_elevenlabs_gate: MagicMock,
) -> None:
    session = MagicMock()
    session.id = "sess_2"
    mock_session.return_value = session

    mock_runner = MagicMock()
    mock_runner.run_async = MagicMock(
        return_value=_async_gen(_make_empty_event()),
    )
    mock_get_runner.return_value = mock_runner

    result = await runner_mod.get_agent_response("u2", "nothing")
    assert "couldn't generate" in result.lower()


@patch("gateway.runner._run_via_elevenlabs", new_callable=AsyncMock)
@patch("gateway.runner._get_runner")
@patch("gateway.runner.create_or_get_session")
async def test_force_adk_empty_never_calls_elevenlabs(
    mock_session: AsyncMock,
    mock_get_runner: MagicMock,
    mock_elevenlabs: AsyncMock,
) -> None:
    session = MagicMock()
    session.id = "sess_3"
    mock_session.return_value = session

    mock_runner = MagicMock()
    mock_runner.run_async = MagicMock(
        return_value=_async_gen(_make_empty_event()),
    )
    mock_get_runner.return_value = mock_runner

    result = await runner_mod.get_agent_response("u3", "hello", force_adk=True)
    mock_elevenlabs.assert_not_called()
    assert "adk swarm" in result.lower()


@patch("gateway.runner._run_via_elevenlabs", new_callable=AsyncMock)
@patch("gateway.runner._get_runner")
@patch("gateway.runner.create_or_get_session")
async def test_malware_sample_prompt_empty_never_calls_elevenlabs(
    mock_session: AsyncMock,
    mock_get_runner: MagicMock,
    mock_elevenlabs: AsyncMock,
) -> None:
    session = MagicMock()
    session.id = "sess_4"
    mock_session.return_value = session

    mock_runner = MagicMock()
    mock_runner.run_async = MagicMock(
        return_value=_async_gen(_make_empty_event()),
    )
    mock_get_runner.return_value = mock_runner

    result = await runner_mod.get_agent_response(
        "u4",
        "analyze the malware sample at /tmp/samples/u/file.js",
    )
    mock_elevenlabs.assert_not_called()
    assert "pantheon analysis" in result.lower()


@patch("gateway.runner._run_via_elevenlabs", new_callable=AsyncMock)
@patch("gateway.runner._get_runner")
@patch("gateway.runner.create_or_get_session")
async def test_activation_phrase_empty_never_calls_elevenlabs(
    mock_session: AsyncMock,
    mock_get_runner: MagicMock,
    mock_elevenlabs: AsyncMock,
) -> None:
    session = MagicMock()
    session.id = "sess_5"
    mock_session.return_value = session

    mock_runner = MagicMock()
    mock_runner.run_async = MagicMock(
        return_value=_async_gen(_make_empty_event()),
    )
    mock_get_runner.return_value = mock_runner

    result = await runner_mod.get_agent_response("u5", "Please analyze malware in this zip")
    mock_elevenlabs.assert_not_called()
    assert "adk swarm" in result.lower()
