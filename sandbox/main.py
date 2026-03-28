"""Hephaestus — FastAPI sandbox service."""
from __future__ import annotations

import logging

import docker
import docker.errors
from fastapi import FastAPI, HTTPException

from sandbox.analyzer import Analyzer
from sandbox.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    IOCReport,
    ThreatReport,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("hephaestus")

app = FastAPI(
    title="Hephaestus",
    description="Pantheon malware sandbox service",
    version="0.1.0",
)

_analyzer = Analyzer()


@app.get("/sandbox/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        client = docker.from_env()
        client.ping()
        docker_ok = True
    except Exception:
        docker_ok = False
    return HealthResponse(status="ok" if docker_ok else "degraded", docker_available=docker_ok)


@app.post("/sandbox/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    job_id = await _analyzer.submit(
        request.file_content_b64,
        request.filename,
        request.analysis_type,
    )
    return AnalyzeResponse(job_id=job_id, status="queued")


@app.get("/sandbox/report/{job_id}", response_model=ThreatReport)
def get_report(job_id: str) -> ThreatReport:
    report = _analyzer.get_report(job_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return report


@app.get("/sandbox/iocs/{job_id}", response_model=IOCReport)
def get_iocs(job_id: str) -> IOCReport:
    iocs = _analyzer.get_iocs(job_id)
    if iocs is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or still running")
    return iocs
