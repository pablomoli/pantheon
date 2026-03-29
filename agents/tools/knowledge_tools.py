"""Static knowledge tools for Pantheon agents.

Provides access to pre-analyzed malware findings from the MALWARE/ corpus.
Used as a fallback when the live sandbox pipeline cannot complete analysis.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Absolute path to the repo root — two levels up from this file.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DISCOVERIES_PATH = _REPO_ROOT / "MALWARE" / "discoveries.md"


def read_malware_analysis() -> str:
    """Return the pre-analyzed reverse engineering report for the active malware sample.

    Reads MALWARE/discoveries.md from the repository. Use this tool when the
    sandbox pipeline is unavailable, slow, or has already completed and you need
    a comprehensive reference of the malware's behavior, IOCs, and kill chain.

    Returns:
        Full text of the malware analysis document, or an error message if
        the file cannot be read.
    """
    try:
        content = _DISCOVERIES_PATH.read_text(encoding="utf-8")
        logger.info("read_malware_analysis: loaded %d chars from %s", len(content), _DISCOVERIES_PATH)
        return content
    except FileNotFoundError:
        logger.warning("read_malware_analysis: %s not found", _DISCOVERIES_PATH)
        return (
            "MALWARE/discoveries.md not found. "
            "Proceed with sandbox analysis results only."
        )
    except OSError as exc:
        logger.error("read_malware_analysis: failed to read %s: %s", _DISCOVERIES_PATH, exc)
        return f"Could not read malware analysis file: {exc}"
