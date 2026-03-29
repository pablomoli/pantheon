# Agents Module

This folder contains the Pantheon multi-agent system built on Google ADK.

Each agent has a focused responsibility in the malware-analysis pipeline:

- Zeus: root orchestrator and user-facing coordinator
- Athena: initial triage and threat classification
- Hades: static and dynamic malware analysis
- Apollo: IOC enrichment and report synthesis
- Ares: containment, remediation, and prevention planning
- Artemis: background sentinel that watches for new samples

## Core Files

- `zeus.py`: root orchestration logic and system prompt
- `athena.py`, `hades.py`, `apollo.py`, `ares.py`: specialist agent definitions
- `artemis.py`: sentinel daemon for autonomous sample discovery
- `worker.py`: background queue/worker integration
- `swarm.py`: job lifecycle/state management for multi-stage execution
- `model_config.py`: model selection and shared LLM config

## Supporting Directories

- `tools/`: tool interfaces used by agents (sandbox calls, reports, memory, remediation)
- `agent_cards/`: agent metadata/config cards
- `tests/`: agent-level tests

## Pipeline Handoff Order

1. Zeus receives a request and triggers Athena.
2. Athena classifies severity/category and hands off to Hades.
3. Hades performs analysis and hands off to Apollo.
4. Apollo enriches findings and hands off to Ares.
5. Ares generates action plans and returns output to Zeus.

## Eventing Expectations

Agents are expected to emit events to the Hephaestus EventBus so the dashboard can visualize:

- Agent activation/completion
- Tool call start/result
- Inter-agent handoffs
- Stage unlocks and IOC/process/network observations

## Local Development

From repository root:

```bash
uv sync
uv run mypy agents
uv run ruff check agents
uv run pytest tests/agents
```

## Design Notes

- Keep agent files focused on orchestration/prompting; push operational logic into `agents/tools`.
- Preserve complete typing annotations and strict mypy compatibility.
- Do not execute malware directly in this layer; use sandbox/VPS tools only.
