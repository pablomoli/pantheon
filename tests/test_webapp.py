"""Tests for gateway.webapp — FastAPI Mini App endpoints."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from gateway.webapp import app

client = TestClient(app)


def test_call_page_returns_html() -> None:
    resp = client.get("/call")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Pantheon" in resp.text


@patch.dict("os.environ", {"ELEVENLABS_AGENT_ID": "test-agent-123"})
def test_agent_config_returns_id() -> None:
    resp = client.get("/api/agent-config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_id"] == "test-agent-123"
