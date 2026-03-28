"""Voice persona configuration."""

from __future__ import annotations

import os

# Default voice — deep, authoritative. Override via ELEVENLABS_VOICE_ID env var.
_DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"


def get_voice_id() -> str:
    """Return the current voice ID, checking env each time for hot-reload."""
    return os.getenv("ELEVENLABS_VOICE_ID") or _DEFAULT_VOICE_ID
