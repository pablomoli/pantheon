"""Gemini and Nova model assignments for each Pantheon agent.

This file is the single source of truth for all AI models used in the system.
You can override these defaults via environment variables in your .env file.
"""
from __future__ import annotations

from itertools import cycle
import os
from threading import Lock

# --- Model Categories ---

# Lightweight: Routing, classification, simple STT fallback.
LITE_MODEL = os.getenv("PANTHEON_LITE_MODEL", "gemini-2.5-flash")

# Medium: Correlating analysis results, IOC enrichment.
MEDIUM_MODEL = os.getenv("PANTHEON_MEDIUM_MODEL", "gemini-2.5-flash")

# Heavy: Final synthesis, high-stakes remediation planning, complex reasoning.
HEAVY_MODEL = os.getenv("PANTHEON_HEAVY_MODEL", "gemini-2.5-flash")


# --- Agent Assignments ---

# Zeus: Root orchestrator. Primary task is routing and compilation.
ZEUS_MODEL = LITE_MODEL

# Athena: Threat classification and ticket creation. Structured and fast.
ATHENA_MODEL = LITE_MODEL

# Hades: Malware analysis. Requires correlating sandbox results.
HADES_MODEL = MEDIUM_MODEL

# Apollo: IOC extraction and threat intelligence enrichment.
APOLLO_MODEL = MEDIUM_MODEL

# Ares: Final containment, remediation, and prevention planning.
ARES_MODEL = HEAVY_MODEL

# Muse (Voice): STT fallback model.
MUSE_STT_MODEL = LITE_MODEL

# GeminiAnalyst (Hephaestus static pipeline): Behavioral inference.
GEMINI_ANALYST_MODEL = LITE_MODEL


def _load_gemini_api_keys() -> list[str]:
	"""Load Gemini API keys in configured priority order.

	Preferred order is GEMINI_API1, GEMINI_API2, GEMINI_API3 so calls rotate
	across the team's free-tier keys. Falls back to GEMINI_API and then
	GOOGLE_API_KEY for backward compatibility.
	"""
	candidates = [
		os.getenv("GEMINI_API1", ""),
		os.getenv("GEMINI_API2", ""),
		os.getenv("GEMINI_API3", ""),
		os.getenv("GEMINI_API", ""),
		os.getenv("GOOGLE_API_KEY", ""),
	]

	keys: list[str] = []
	for key in candidates:
		if key and key not in keys:
			keys.append(key)
	return keys


_GEMINI_API_KEYS: list[str] = _load_gemini_api_keys()
_GEMINI_KEY_CYCLE = cycle(_GEMINI_API_KEYS) if _GEMINI_API_KEYS else None
_GEMINI_KEY_LOCK = Lock()


def get_next_gemini_api_key() -> str:
	"""Return the next Gemini API key in round-robin order.

	Rotation order is 1 -> 2 -> 3 -> repeat when GEMINI_API1..3 are set.
	"""
	if _GEMINI_KEY_CYCLE is None:
		raise RuntimeError(
			"No Gemini API key configured. Set GEMINI_API1..3, GEMINI_API, or GOOGLE_API_KEY."
		)

	with _GEMINI_KEY_LOCK:
		return next(_GEMINI_KEY_CYCLE)
