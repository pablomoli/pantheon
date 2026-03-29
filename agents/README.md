# Agents Module

This folder contains the Pantheon multi-agent system built on Google ADK.

Each agent has a focused responsibility in the malware-analysis pipeline:

- **Zeus**: root orchestrator and user-facing coordinator
- **Athena**: initial triage and threat classification
- **Hades**: static and dynamic malware analysis (Docker sandbox + Windows VPS)
- **Apollo**: IOC enrichment, threat intel correlation, and report synthesis
- **Ares**: containment, remediation, and prevention planning (parallel sub-agents)
- **Artemis**: background sentinel that watches for new samples
- **Impact Agent**: remote A2A specialist for critical infrastructure assessment

## Core Files

- `zeus.py`: root orchestration logic and system prompt
- `athena.py`: triage agent — severity classification, incident ticket creation
- `hades.py`: analysis agent — Docker sandbox + Windows VPS detonation integration
- `apollo.py`: intelligence agent — IOC extraction, Gemini enrichment, prior-run synthesis
- `ares.py`: response agent — delegates to parallel sub-agents
- `artemis.py`: sentinel daemon for autonomous sample discovery
- `impact_agent.py`: remote A2A impact assessment specialist (deployed on Cloud Run)
- `prompts.py`: shared system prompts and instruction templates
- `model_config.py`: model selection and shared LLM config
- `worker.py`: background queue/worker integration
- `swarm.py`: job lifecycle/state management (queued → running → done FSM)
- `server.py`: ADK server entry point for Cloud Run deployment

## Ares Sub-Agent Architecture

Ares uses a ParallelAgent + LoopAgent pattern:

- `ares_containment.py`: network isolation, process termination, firewall rules
- `ares_remediation.py`: file cleanup, registry repair, credential rotation
- `ares_prevention.py`: YARA rules, Sigma detection, GPO hardening, EDR tuning
- `ares_assembler.py`: merges parallel outputs into a single incident report
- `ares_verifier.py`: validates plans against evidence from Hades/Apollo
- `ares_reviser.py`: corrects flagged issues (LoopAgent, max 2 iterations)
- `ares_workflow.py`: orchestrates the parallel → verify → revise pipeline
- `ares_workflow_support.py`: helper utilities for Ares workflow

## Supporting Directories

- `tools/`: tool interfaces used by agents
  - `sandbox_tools.py` — submit_sample, poll_report, get_report, get_iocs
  - `report_tools.py` — format_threat_report, enrich_iocs_with_threat_intel
  - `remediation_tools.py` — containment/remediation/prevention plan generators
  - `event_tools.py` — emit_event() helper for EventBus telemetry
  - `vps_tools.py` — Windows VPS detonation via SSH (Procmon, FakeNet-NG, Wireshark)
  - `memory_tools.py` — KnowledgeStore: store/load agent memory, behavioral fingerprints
  - `triage_tools.py` — severity classification and routing utilities
- `agent_cards/`: agent metadata cards (JSON) — one per god (Zeus, Hermes, Athena, Hades, Apollo, Ares, Artemis, Hephaestus)
- `tests/`: agent-level tests
- `.adk/`: ADK configuration

## Pipeline Handoff Order

1. Zeus receives a request and triggers Athena.
2. Athena classifies severity/category and hands off to Hades.
3. Hades performs analysis (Docker + optional VPS detonation) and hands off to Apollo.
4. Apollo enriches findings, calls remote impact specialist via A2A, and hands off to Ares.
5. Ares runs containment, remediation, and prevention in parallel (ParallelAgent).
6. Ares verifier/reviser loop validates and corrects plans (LoopAgent, max 2 iterations).
7. Ares assembler compiles the final report and returns to Zeus.

## Event Emission

Every agent action emits events to the Hephaestus EventBus via `emit_event()` (from `tools/event_tools.py`):

- `AGENT_ACTIVATED` / `AGENT_COMPLETED` — agent entry/exit
- `TOOL_CALLED` / `TOOL_RESULT` — before/after every tool call
- `HANDOFF` — inter-agent transfers
- `STAGE_UNLOCKED` — attack chain stage progression
- `IOC_DISCOVERED` / `PROCESS_EVENT` / `NETWORK_EVENT` — telemetry observations

## Local Development

From repository root:

```bash
uv sync
uv run mypy agents
uv run ruff check agents
uv run pytest tests/agents agents/tests
```

## Design Notes

- Keep agent files focused on orchestration/prompting; push operational logic into `agents/tools/`.
- Preserve complete typing annotations and strict mypy compatibility.
- `from __future__ import annotations` at the top of every file.
- Do not execute malware directly in this layer; use sandbox/VPS tools only.
- Use Pydantic v2 models for all data contracts.
