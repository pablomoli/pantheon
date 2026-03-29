"""LLM-powered malware analysis — sends deobfuscated content for behavioural inference."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, cast

from agents.model_config import GEMINI_ANALYST_MODEL, MAX_OUTPUT_TOKENS_LITE
from agents.openrouter_client import openrouter_chat
from sandbox.models import FileIOCs, NetworkIOCs, RiskLevel, ThreatReport

_MODEL = GEMINI_ANALYST_MODEL

logger = logging.getLogger(__name__)

_ANALYSIS_PROMPT = """\
You are a malware analyst. The following are strings and patterns extracted
from an obfuscated JavaScript malware sample.

Analyze this content and respond ONLY with a JSON object matching this exact schema:
{
  "malware_type": "string — e.g. WSH dropper, ransomware loader, keylogger",
  "obfuscation_technique": "string — describe the obfuscation method",
  "behavior": ["array of strings — observed or inferred behaviors"],
  "risk_level": "critical | high | medium | low",
  "affected_systems": ["array — Windows workstations, servers, browsers, etc."],
  "network_iocs": {
    "ips": ["list of malicious IPs"],
    "domains": ["list of malicious domains"],
    "ports": [list of integer ports],
    "protocols": ["list of protocols"],
    "urls": ["list of full URLs"]
  },
  "registry_iocs": ["list of registry keys"],
  "remediation_hints": ["list of concrete remediation steps"]
}

Extracted content:
"""


class GeminiAnalyst:
    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key

    async def analyze(self, summary_text: str) -> ThreatReport:
        """Send extracted strings to the LLM and parse the response into a ThreatReport."""
        prompt = _ANALYSIS_PROMPT + summary_text[:12000]  # cap context
        try:
            raw = await self._call_llm(prompt)
            return self._parse_response(raw)
        except Exception as exc:
            logger.warning("LLM analysis failed: %s", exc)
            return self._fallback_report(str(exc))

    async def _call_llm(self, prompt: str) -> str:
        return await openrouter_chat(
            model=_MODEL,
            user_prompt=prompt,
            temperature=0.2,
            max_tokens=min(4096, MAX_OUTPUT_TOKENS_LITE),
            json_mode=True,
            api_key=self._api_key,
        )

    def _parse_response(self, raw: str) -> ThreatReport:
        # Strip markdown code fences if present
        text = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data: dict[str, Any] = json.loads(text)
        except json.JSONDecodeError:
            # The model sometimes emits bare backslashes in Windows paths that are
            # invalid JSON escapes (e.g. \S, \u not followed by 4 hex digits).
            sanitized = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r"/", text)
            data = json.loads(sanitized)

        net = data.get("network_iocs", {})
        return ThreatReport(
            job_id="",  # filled in by analyzer.py
            status="complete",
            malware_type=data.get("malware_type", "unknown"),
            obfuscation_technique=data.get("obfuscation_technique", "unknown"),
            behavior=data.get("behavior", []),
            network_iocs=NetworkIOCs(
                ips=net.get("ips", []),
                domains=net.get("domains", []),
                ports=net.get("ports", []),
                protocols=net.get("protocols", []),
                urls=net.get("urls", []),
            ),
            file_iocs=FileIOCs(),
            registry_iocs=data.get("registry_iocs", []),
            risk_level=_safe_risk(data.get("risk_level", "medium")),
            affected_systems=data.get("affected_systems", []),
            gemini_summary=raw[:2000],
            remediation_hints=data.get("remediation_hints", []),
        )

    def _fallback_report(self, error: str) -> ThreatReport:
        return ThreatReport(
            job_id="",
            status="complete",
            malware_type="unknown — LLM analysis failed",
            obfuscation_technique="unknown",
            behavior=[f"LLM error: {error}"],
            network_iocs=NetworkIOCs(),
            file_iocs=FileIOCs(),
            registry_iocs=[],
            risk_level="high",
            affected_systems=["unknown"],
            gemini_summary=error,
            remediation_hints=["Manual analysis required"],
        )


def _safe_risk(value: str) -> RiskLevel:
    if value in ("low", "medium", "high", "critical"):
        return cast(RiskLevel, value)
    return "high"
