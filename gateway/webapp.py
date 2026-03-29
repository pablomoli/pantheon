"""FastAPI web app — serves the voice-call Mini App and agent tool webhooks.

Runs alongside the Telegram bot so that Telegram's WebApp iframe can load
the call page and connect directly to ElevenLabs Conversational AI.

The /api/tools/* endpoints are registered as **custom tools** on the
ElevenLabs agent, allowing the voice agent to trigger sandbox analysis
and retrieve reports during a live call.
"""

from __future__ import annotations

import base64
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="Pantheon — Hermes WebApp")

# ElevenLabs JS SDK needs CORS to hit /api/* from the Mini App iframe.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATIC_DIR = Path(__file__).parent / "static"
_SAMPLES_DIR = Path(os.getenv("SAMPLES_DIR", "/tmp/samples"))


# ---------------------------------------------------------------------------
# Mini App pages
# ---------------------------------------------------------------------------


@app.get("/call")
async def call_page() -> FileResponse:
    """Serve the voice-call Mini App HTML."""
    return FileResponse(_STATIC_DIR / "call.html", media_type="text/html")


@app.get("/api/agent-config")
async def agent_config() -> JSONResponse:
    """Return the ElevenLabs agent ID so the Mini App can connect."""
    agent_id = os.getenv("ELEVENLABS_AGENT_ID", "")
    return JSONResponse({"agent_id": agent_id})


# Serve static assets from gateway/static/.
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
