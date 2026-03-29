import base64
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Fallback to local MALWARE repository since "we only have one malware which is already loaded to vultr"
_SAMPLES_DIR = Path(os.getenv("SAMPLES_DIR", "/Users/sairamen/projects/pantheon/MALWARE"))


async def tool_analyze(parameters: dict[str, Any]) -> str:
    """Webhook: trigger sandbox analysis on the malware sample.
    The ElevenLabs agent calls this when the user says something like
    'analyze the malware sample' during a voice call.
    """
    filename = parameters.get("filename", "")

    sample_path: Path | None = None
    if filename:
        for candidate in _SAMPLES_DIR.rglob(filename):
            sample_path = candidate
            break

    if sample_path is None:
        # User didn't specify filename or it wasn't found - try to grab the exact known malicious file, or fallback to newest
        known_sample = _SAMPLES_DIR / "6108674530.JS.malicious"
        if known_sample.exists() and known_sample.is_file():
            sample_path = known_sample
        else:
            all_samples = sorted(
                _SAMPLES_DIR.rglob("*"), key=lambda p: p.stat().st_mtime, reverse=True
            )
            for s in all_samples:
                if s.is_file():
                    sample_path = s
                    break

    if sample_path is None:
        return json.dumps(
            {
                "status": "error",
                "message": "No sample found. Upload a file through Telegram first, then ask me to analyze it.",
            }
        )

    job_id = str(uuid.uuid4())[:8]
    file_b64 = base64.b64encode(sample_path.read_bytes()).decode()

    sandbox_url = os.getenv("SANDBOX_API_URL", "http://localhost:9000")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{sandbox_url}/sandbox/analyze",
                json={
                    "job_id": job_id,
                    "file_content_b64": file_b64,
                    "filename": sample_path.name,
                    "analysis_type": parameters.get("analysis_type", "both"),
                },
            )
            result = resp.json()
            logger.info("Sandbox accepted job %s: %s", job_id, result)
            return json.dumps(
                {
                    "status": "submitted",
                    "job_id": job_id,
                    "filename": sample_path.name,
                    "message": f"Analysis started for {sample_path.name}. Job ID is {job_id}. I'll check the results once the analysis completes.",
                }
            )
    except Exception:
        logger.exception("Sandbox not reachable — running ADK fallback for %s", sample_path.name)
        # Fallback to ADK
        from gateway.runner import get_agent_response

        response = await get_agent_response(
            "voice-call-user",
            f"analyze the malware sample at {sample_path}",
        )
        return json.dumps(
            {
                "status": "complete",
                "job_id": job_id,
                "filename": sample_path.name,
                "message": response,
            }
        )


async def tool_report(parameters: dict[str, Any]) -> str:
    """Webhook: retrieve analysis report for a job."""
    job_id = parameters.get("job_id", "")
    if not job_id:
        # In a conversational loop, sometimes the agent might miss the exact job ID to query.
        return json.dumps(
            {
                "status": "error",
                "message": "Please specify the job ID from the analysis you started.",
            }
        )

    sandbox_url = os.getenv("SANDBOX_API_URL", "http://localhost:9000")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{sandbox_url}/sandbox/report/{job_id}")
            return json.dumps(resp.json())
    except Exception:
        logger.exception("Could not retrieve report for job %s", job_id)
        return json.dumps(
            {
                "status": "error",
                "message": f"Report for job {job_id} is not available yet. The analysis may still be running.",
            }
        )


async def tool_status(parameters: dict[str, Any]) -> str:
    """Webhook: check if the sandbox is healthy and ready."""
    sandbox_url = os.getenv("SANDBOX_API_URL", "http://localhost:9000")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{sandbox_url}/sandbox/health")
            return json.dumps(resp.json())
    except Exception:
        return json.dumps(
            {
                "status": "degraded",
                "docker_available": False,
                "message": "Sandbox service is not reachable. Analysis will use the AI pipeline instead.",
            }
        )
