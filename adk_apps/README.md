# ADK Apps

This folder contains Google ADK application definitions used for Cloud Run deployment and the ADK Dev UI.

Each subdirectory is a self-contained ADK app that can be served via `google.adk.cli` or deployed as a Cloud Run service.

## Structure

### `pantheon_agent/`

The main Pantheon agent tree — wires up Zeus as the root orchestrator with all sub-agents (Athena, Hades, Apollo, Ares) and tools.

- `agent.py`: ADK app entry point — imports and exposes the Zeus agent
- `__init__.py`: package marker

This app is deployed to Cloud Run with:
- ADK Dev UI enabled (`web=True`) — judges can inspect the agent tree and traces
- A2A protocol enabled (`a2a=True`) — supports inter-service agent calls

### `impact_agent/`

A standalone A2A specialist for critical infrastructure impact assessment. Deployed as a separate Cloud Run service.

- `agent.py`: ADK app entry point — imports the impact assessment agent
- `agent.json`: A2A agent card (`.well-known/agent.json`) — declares the agent's identity and capabilities for discovery
- `__init__.py`: package marker

Apollo calls this remote agent via A2A during the intelligence phase to assess infrastructure continuity risk.

## Deployment

Both apps are deployed via `infra/cloud-deploy.sh`:

```bash
export GCP_PROJECT_ID=your-project-id
./infra/cloud-deploy.sh
```

Live URLs (after deployment):

| Surface | Description |
| --- | --- |
| ADK Dev UI | `https://pantheon-agents-<hash>-uc.a.run.app/dev-ui/` |
| Pantheon agent API | `https://pantheon-agents-<hash>-uc.a.run.app` |
| Impact agent (A2A) | `https://impact-agent-<hash>-uc.a.run.app` |

## Local Development

Run the ADK Dev UI locally:

```bash
uv run adk web adk_apps/pantheon_agent
```

For the impact agent:

```bash
uv run adk web adk_apps/impact_agent --port 8001
```

## Environment

The A2A wiring URL is configured via:

```bash
PANTHEON_IMPACT_AGENT_CARD_URL=http://localhost:8001/.well-known/agent.json  # local
# Automatically set by cloud-deploy.sh for production
```
