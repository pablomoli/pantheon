"""HTTP tools for calling the Hephaestus sandbox service.

All functions are async and use httpx. They return JSON-serializable dicts
so that google-adk can pass results back to the LLM.
"""

from __future__ import annotations

import asyncio
import base64
import os
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any

import httpx

from agents.tools.event_tools import emit_event
from sandbox.models import (
    AgentName,
    AnalyzeRequest,
    AnalyzeResponse,
    EventType,
    HealthResponse,
    IOCReport,
    ThreatReport,
)

_SANDBOX_URL: str = os.getenv("SANDBOX_API_URL", "http://localhost:9000")
_POLL_INTERVAL: float = 2.0
_MAX_POLLS: int = 30
_SUPPRESS_REPORT_EVENTS: ContextVar[bool] = ContextVar(
    "_SUPPRESS_REPORT_EVENTS",
    default=False,
)


def _resolve_sample_path(file_path: str) -> Path:
    """Resolve a sample path across host/docker conventions.

    The LLM may sometimes provide container-style paths like ``/samples/...``
    or stale absolute paths from another workstation. This resolver keeps
    analysis robust by trying sane local fallbacks.
    """
    requested = Path(file_path).expanduser()
    if requested.exists() and requested.is_file():
        return requested

    candidates: list[Path] = []

    # Shared sample upload directory used by Hermes.
    samples_root = Path(os.getenv("SAMPLES_DIR", "/tmp/samples"))
    if samples_root.exists():
        candidates.append(samples_root / requested.name)
        candidates.extend(samples_root.glob(f"**/{requested.name}"))

    # Repo-local malware corpus fallback for demo mode.
    repo_root = Path(__file__).resolve().parents[2]
    malware_dir = repo_root / "MALWARE"
    if malware_dir.exists():
        candidates.append(malware_dir / requested.name)
        candidates.append(malware_dir / "6108674530.JS.malicious")

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    raise FileNotFoundError(
        f"Sample file not found: {file_path}. "
        "Upload a file via Hermes or set SAMPLES_DIR to the upload location."
    )


async def submit_sample(file_path: str, analysis_type: str = "both") -> dict[str, str]:
    """Submit a malware sample to the Hephaestus sandbox for analysis.

    Reads the file at *file_path*, base64-encodes it, generates a unique job
    ID, and posts an AnalyzeRequest to POST /sandbox/analyze.

    Args:
        file_path: Absolute path to the malware sample on disk.
        analysis_type: Pipeline(s) to run — "static", "dynamic", or "both".

    Returns:
        Dict with ``job_id`` (str) and ``status`` ("queued" or "running").
    """
    await emit_event(
        EventType.TOOL_CALLED,
        agent=AgentName.HADES,
        tool="submit_sample",
        payload={"file_path": file_path, "analysis_type": analysis_type},
    )
    path = _resolve_sample_path(file_path)
    raw_bytes = path.read_bytes()
    b64 = base64.b64encode(raw_bytes).decode()
    job_id = str(uuid.uuid4())

    request = AnalyzeRequest(
        job_id=job_id,
        file_content_b64=b64,
        filename=path.name,
        analysis_type=analysis_type,  # type: ignore[arg-type]
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{_SANDBOX_URL}/sandbox/analyze",
            json=request.model_dump(),
        )
        resp.raise_for_status()
        result = AnalyzeResponse.model_validate(resp.json())

    await emit_event(
        EventType.TOOL_RESULT,
        agent=AgentName.HADES,
        tool="submit_sample",
        job_id=result.job_id,
        payload={"job_id": result.job_id, "status": result.status},
    )
    return {"job_id": result.job_id, "status": result.status}


async def _fetch_report(job_id: str) -> dict[str, Any]:  # Any: pydantic model_dump()
    """Fetch the raw ThreatReport from the sandbox without emitting events.

    Used internally by :func:`get_report` and :func:`poll_report` to avoid
    spurious TOOL_CALLED/TOOL_RESULT events on every poll iteration.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{_SANDBOX_URL}/sandbox/report/{job_id}")
        resp.raise_for_status()
        report = ThreatReport.model_validate(resp.json())
    return report.model_dump()
async def get_report(job_id: str) -> dict[str, Any]:  # Any: pydantic model_dump()
    """Fetch the current threat analysis report for a sandbox job.

    Calls GET /sandbox/report/{job_id}. Status may be ``queued``, ``running``,
    ``complete``, or ``failed``.

    Args:
        job_id: Job identifier returned from :func:`submit_sample`.

    Returns:
        Dict representation of :class:`~sandbox.models.ThreatReport`.
    """
    if not _SUPPRESS_REPORT_EVENTS.get():
        await emit_event(
            EventType.TOOL_CALLED,
            agent=AgentName.HADES,
            tool="get_report",
            job_id=job_id,
            payload={"job_id": job_id},
        )
    report = await _fetch_report(job_id)
    if not _SUPPRESS_REPORT_EVENTS.get():
        await emit_event(
            EventType.TOOL_RESULT,
            agent=AgentName.HADES,
            tool="get_report",
            job_id=job_id,
            payload={"status": report.get("status")},
        )
    return report


async def get_iocs(job_id: str) -> dict[str, Any]:  # Any: pydantic model_dump()
    """Fetch the flat IOC list for a completed sandbox job.

    Calls GET /sandbox/iocs/{job_id}.

    Args:
        job_id: Job identifier returned from :func:`submit_sample`.

    Returns:
        Dict representation of :class:`~sandbox.models.IOCReport` with keys
        ``ips``, ``domains``, ``file_hashes``, ``file_paths``, ``ports``,
        ``registry_keys``, ``cve_ids``, and ``urls``.
    """
    await emit_event(
        EventType.TOOL_CALLED,
        agent=AgentName.APOLLO,
        tool="get_iocs",
        job_id=job_id,
        payload={"job_id": job_id},
    )
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{_SANDBOX_URL}/sandbox/iocs/{job_id}")
        resp.raise_for_status()
        ioc_report = IOCReport.model_validate(resp.json())
    ioc_report_dict = ioc_report.model_dump()
    await emit_event(
        EventType.TOOL_RESULT,
        agent=AgentName.APOLLO,
        tool="get_iocs",
        job_id=job_id,
        payload={
            "ip_count": len(ioc_report_dict.get("ips", [])),
            "domain_count": len(ioc_report_dict.get("domains", [])),
        },
    )
    return ioc_report_dict


async def poll_report(job_id: str) -> dict[str, Any]:  # Any: pydantic model_dump()
    """Poll the sandbox until a job finishes, then return the full ThreatReport.

    Polls GET /sandbox/report/{job_id} every two seconds for up to 60 seconds.
    Returns as soon as status is ``complete`` or ``failed``.

    Args:
        job_id: Job identifier returned from :func:`submit_sample`.

    Returns:
        Dict representation of :class:`~sandbox.models.ThreatReport` with
        ``status`` equal to ``"complete"`` or ``"failed"``.

    Raises:
        TimeoutError: The job did not complete within the polling window.
        httpx.HTTPStatusError: The sandbox returned an HTTP error response.
    """
    await emit_event(
        EventType.TOOL_CALLED,
        agent=AgentName.HADES,
        tool="poll_report",
        payload={"job_id": job_id},
    )
    token = _SUPPRESS_REPORT_EVENTS.set(True)
    try:
        for _ in range(_MAX_POLLS):
            report = await get_report(job_id)
            if report.get("status") in ("complete", "failed"):
                await emit_event(
                    EventType.TOOL_RESULT,
                    agent=AgentName.HADES,
                    tool="poll_report",
                    job_id=job_id,
                    payload={"status": report.get("status")},
                )
                return report
            await asyncio.sleep(_POLL_INTERVAL)
    finally:
        _SUPPRESS_REPORT_EVENTS.reset(token)

    raise TimeoutError(
        f"Sandbox job {job_id!r} did not complete within "
        f"{_MAX_POLLS * _POLL_INTERVAL:.0f} seconds."
    )


async def check_sandbox_health() -> dict[str, Any]:  # Any: health json payload
    """Check whether the Hephaestus sandbox service and Docker daemon are up.

    Calls GET /sandbox/health.

    Returns:
        Dict with ``status`` ("ok" or "degraded"), ``docker_available`` (bool),
        and ``version`` (str).
    """
    await emit_event(
        EventType.TOOL_CALLED,
        agent=AgentName.HADES,
        tool="check_sandbox_health",
        payload={},
    )
    health_dict: dict[str, Any]
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{_SANDBOX_URL}/sandbox/health")
            resp.raise_for_status()
        health = HealthResponse.model_validate(resp.json())
        health_dict = health.model_dump()
    except httpx.HTTPError as exc:
        err = str(exc).strip() or exc.__class__.__name__
        health_dict = {
            "status": "degraded",
            "docker_available": False,
            "version": "unknown",
            "error": err,
        }
    await emit_event(
        EventType.TOOL_RESULT,
        agent=AgentName.HADES,
        tool="check_sandbox_health",
        payload={
            "status": health_dict.get("status"),
            "docker_available": health_dict.get("docker_available"),
        },
    )
    return health_dict
