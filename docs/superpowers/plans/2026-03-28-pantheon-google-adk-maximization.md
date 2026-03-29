# Pantheon — Google ADK Challenge Maximization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Maximize Pantheon's competitiveness for the Google Cloud ADK challenge without destabilizing the core NextEra malware-analysis demo. The highest-value additions are: a real ADK runtime surface with Dev UI, one real `ParallelAgent`, one real `LoopAgent`, and one visible A2A handshake with a remote specialist agent.

**Architecture:** Keep the existing specialist Pantheon agents (`zeus`, `athena`, `hades`, `apollo`, `ares`) as the domain brains. Do **not** rewrite them from scratch. Instead, wrap them with workflow agents where the work is naturally parallel or iterative. The recommended demo path is:

1. `Zeus` remains the top-level LLM orchestrator.
2. `Ares` becomes a workflow composed of:
   - a `ParallelAgent` fanout for containment / remediation / prevention planning
   - a `LoopAgent` for verifier-driven self-correction
   - an assembler that emits the final incident response document
3. A remote A2A specialist agent performs mission-impact analysis for critical infrastructure continuity.
4. The ADK Dev UI is exposed on a public Google Cloud URL so judges can see the literal trace and workflow branching.

**Tech Stack:** Python 3.12, `uv`, `google-adk`, FastAPI, ADK `SequentialAgent` / `ParallelAgent` / `LoopAgent`, ADK A2A (Python, experimental), existing Pantheon EventBus, existing sandbox + VPS tools, Cloud Run

**Non-goals:**
- Do not break the primary NextEra malware pipeline.
- Do not replace real tool calls with fake "agent chatter."
- Do not add multiple remote specialists unless the first A2A handshake is already working.
- Do not add workflow agents where the workflow is not meaningfully parallel or iterative.

---

## Progress

| Task | Status | Notes |
|---|---|---|
| 1: Existing specialist Pantheon agents | DONE | Zeus/Athena/Hades/Apollo/Ares already exist |
| 2: Live event stream and dashboard substrate | DONE | EventBus + `/ws` + `/events` already exist |
| 3: ADK runtime surface + Dev UI | pending | No ADK app server in repo today |
| 4: `Ares` `ParallelAgent` wrapper | pending | Highest-ROI workflow migration |
| 5: `Ares` `LoopAgent` self-correction | pending | Highest-ROI "autonomy" addition |
| 6: Remote A2A impact specialist | pending | Strongest visibility gain after Dev UI |
| 7: `Hades` parallel fanout (sandbox + VPS) | pending (stretch) | Good, but riskier than Ares |
| 8: `Apollo` evidence loop | pending (stretch) | Good, but less visible than Ares |
| 9: Cloud Run deployment + public URL | pending | Critical for Google judging |
| 10: Demo trace + pitch tuning | pending | Must make the ADK work legible |

---

## Repo Reality Check

Before implementing anything, align on the current state of the repo:

- Existing agent code is in `agents/`.
- Existing tool and event infrastructure is already real and useful.
- `run.py` currently starts only Hephaestus (`sandbox.main:app`).
- `gateway/` is not present in the current checkout.
- `infra/docker-compose.yml` currently comments out the `agents`, `gateway`, and `nginx` services.
- `infra/Dockerfile.agents` points at `agents.server:app`, but that module does not exist yet.

This means the **first Google-track deliverable is not another agent**. It is an **actual ADK runtime surface** the judges can open.

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `adk_apps/pantheon_agent/__init__.py` | create | Package marker for ADK-discoverable Pantheon root app |
| `adk_apps/pantheon_agent/agent.py` | create | Exports `root_agent` for ADK Dev UI / API |
| `adk_apps/impact_agent/__init__.py` | create | Package marker for remote A2A specialist |
| `adk_apps/impact_agent/agent.py` | create | Exports `root_agent` for the remote impact specialist |
| `agents/server.py` | create | FastAPI entrypoint using `get_fast_api_app(..., web=True)` |
| `agents/ares_containment.py` | create | Planner agent focused only on containment |
| `agents/ares_remediation.py` | create | Planner agent focused only on remediation |
| `agents/ares_prevention.py` | create | Planner agent focused only on prevention |
| `agents/ares_verifier.py` | create | Verifier agent for evidence-backed plan checks |
| `agents/ares_reviser.py` | create | Revision agent that fixes verifier findings |
| `agents/ares_assembler.py` | create | Final assembly agent for the full Ares report |
| `agents/ares_workflow.py` | create | `ParallelAgent` + `LoopAgent` wrapper around Ares planning |
| `agents/impact_agent.py` | create | Pantheon-side specialist definition for mission-impact reasoning |
| `agents/hades_workflow.py` | create (stretch) | Parallel wrapper around sandbox + VPS analysis branches |
| `agents/apollo_verifier.py` | create (stretch) | Evidence critic for IOC enrichment |
| `agents/apollo_reviser.py` | create (stretch) | Revision agent for Apollo loop |
| `agents/apollo_workflow.py` | create (stretch) | `LoopAgent` wrapper for Apollo |
| `agents/zeus.py` | modify | Route through workflow wrappers and remote specialist |
| `sandbox/models.py` | modify (optional) | Add one new `AgentName` if the remote specialist must appear on the dashboard graph |
| `frontend/` | modify (optional, Sai) | Show loop iteration and A2A node/edge clearly |
| `infra/Dockerfile.agents` | modify | Build and run ADK app server |
| `infra/docker-compose.yml` | modify | Enable `agents` service for local verification |
| `infra/nginx.conf` | modify | Expose ADK app / UI path if using nginx locally |
| `infra/deploy.sh` | modify | Deploy ADK server along with sandbox |
| `README.md` | modify | Add Google-track runbook / public URL instructions |
| `tests/agents/test_ares_workflow.py` | create | Tests for `ParallelAgent` / loop wiring |
| `tests/agents/test_adk_server.py` | create | Tests for ADK app server bootstrapping |
| `tests/agents/test_hades_workflow.py` | create (stretch) | Tests for sandbox/VPS parallel wrapper |

---

## Task 1: Create an Actual ADK Runtime Surface + Dev UI

**Files:**
- Create: `adk_apps/pantheon_agent/__init__.py`, `adk_apps/pantheon_agent/agent.py`
- Create: `agents/server.py`
- Modify: `infra/Dockerfile.agents`, `infra/docker-compose.yml`, `infra/nginx.conf`, `infra/deploy.sh`

This is the highest-leverage task. Judges cannot reward ADK runtime mastery if there is no ADK runtime surface they can open.

- [ ] **Step 1: Create an ADK-discoverable app folder for Pantheon**

`adk_apps/pantheon_agent/agent.py` should export a single `root_agent`.

Recommended initial shape:

```python
from __future__ import annotations

from agents.zeus import zeus

root_agent = zeus
```

Do not overcomplicate this first version. The point is to make Pantheon visible in the ADK UI immediately.

- [ ] **Step 2: Create `agents/server.py` using ADK's FastAPI helper**

Follow the official Cloud Run / FastAPI pattern with `get_fast_api_app(...)` and `web=True`.

Recommended shape:

```python
from __future__ import annotations

import os

from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "adk_apps")
SESSION_SERVICE_URI = "sqlite+aiosqlite:///./sessions.db"

app: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=["*"],
    web=True,
)
```

Note:
- Verify exact import names against the installed `google-adk` version before coding.
- The path given to `agents_dir` must point at folders that expose `root_agent`.

- [ ] **Step 3: Make the agents container actually boot**

Right now `infra/Dockerfile.agents` references `agents.server:app`, but the module is missing. Once `agents/server.py` exists:

- keep the container entrypoint as `uvicorn agents.server:app`
- enable the `agents` service in `infra/docker-compose.yml`
- expose it on a stable port (`8001` is fine)

- [ ] **Step 4: Verify the UI locally**

Success criteria:
- the ADK web UI loads
- Pantheon appears in the app dropdown
- a single prompt can be submitted to the root agent
- the session persists across reloads

- [ ] **Step 5: Commit**

```bash
git add adk_apps/pantheon_agent/__init__.py adk_apps/pantheon_agent/agent.py \
  agents/server.py infra/Dockerfile.agents infra/docker-compose.yml \
  infra/nginx.conf infra/deploy.sh
git commit -m "feat: add ADK app server and Dev UI surface for Pantheon"
```

---

## Task 2: Migrate `Ares` to a Real `ParallelAgent`

**Files:**
- Create: `agents/ares_containment.py`, `agents/ares_remediation.py`, `agents/ares_prevention.py`
- Create: `agents/ares_assembler.py`
- Create: `agents/ares_workflow.py`
- Modify: `agents/zeus.py` (or the Pantheon root app wrapper) to call the workflow instead of the monolithic `ares`

This is the cleanest workflow-agent migration in the repo. The three planning tasks are naturally independent once the threat summary exists.

- [ ] **Step 1: Split the existing Ares responsibilities into three specialist planner agents**

Each planner should be narrow:
- `ares_containment` only calls `generate_containment_plan`
- `ares_remediation` only calls `generate_remediation_plan`
- `ares_prevention` only calls `generate_prevention_plan`

Each planner should write its output into state under a stable key. Use exact state/output APIs from the installed ADK version.

- [ ] **Step 2: Create an assembler agent**

`ares_assembler` should:
- read the three plan outputs from state
- call `build_full_response`
- store the assembled response via `store_agent_output`
- return the final incident response document

- [ ] **Step 3: Wrap the three planners in `ParallelAgent`**

Recommended workflow shape:

```python
ares_planning_parallel = ParallelAgent(
    name="ares_planning_parallel",
    sub_agents=[
        ares_containment,
        ares_remediation,
        ares_prevention,
    ],
)
```

Then embed that inside a sequential wrapper:

```python
ares_workflow = SequentialAgent(
    name="ares_workflow",
    sub_agents=[
        ares_planning_parallel,
        ares_assembler,
    ],
)
```

Verify exact constructor argument names in the current ADK docs before implementation.

- [ ] **Step 4: Emit visibly useful event payloads**

Do **not** change the event schema unless necessary. Reuse existing events with richer payloads:
- `payload["workflow"] = "ares"`
- `payload["branch"] = "containment" | "remediation" | "prevention"`

This lets the custom dashboard and the event feed show the three branches clearly.

- [ ] **Step 5: Verify the judge-visible outcome**

The ADK UI should visibly show three parallel Ares branches.

The custom dashboard should show:
- three tool/planner activations in close temporal proximity
- one assembled final response afterward

- [ ] **Step 6: Commit**

```bash
git add agents/ares_containment.py agents/ares_remediation.py \
  agents/ares_prevention.py agents/ares_assembler.py agents/ares_workflow.py \
  agents/zeus.py
git commit -m "feat: wrap Ares planning in a ParallelAgent workflow"
```

---

## Task 3: Add a Real `LoopAgent` for Ares Self-Correction

**Files:**
- Create: `agents/ares_verifier.py`
- Create: `agents/ares_reviser.py`
- Modify: `agents/ares_workflow.py`

This is the single best answer to Google's self-correction requirement.

- [ ] **Step 1: Create a verifier agent**

The verifier's job is not to rewrite the plan. Its job is to judge plan quality against evidence already produced by Pantheon.

Verifier checks:
- every urgent action references real malware behavior, IOC, or affected system
- no invented registry keys, file paths, or commands appear
- every plan section is specific enough to be operationally useful
- unsupported claims are downgraded or flagged for rewrite

Output:
- `approved: true|false`
- `findings: list[str]`
- `missing_evidence: list[str]`

- [ ] **Step 2: Create a reviser agent**

The reviser reads:
- the original Ares assembled response
- verifier findings
- the underlying threat summary / IOCs

It returns a corrected response without inventing new evidence.

- [ ] **Step 3: Wrap verifier + reviser in a `LoopAgent`**

Recommended shape:

```python
ares_refinement_loop = LoopAgent(
    name="ares_refinement_loop",
    sub_agents=[ares_verifier, ares_reviser],
    max_iterations=2,
)
```

The verifier should exit the loop early when the response is acceptable. Verify the exact ADK pattern for loop exit in the installed version before coding.

- [ ] **Step 4: Add iteration visibility**

Emit payload fields like:
- `payload["workflow"] = "ares_refinement"`
- `payload["iteration"] = 1`
- `payload["verdict"] = "retry" | "approved"`

This makes the self-correction legible in both the ADK UI and the custom event feed.

- [ ] **Step 5: Update the workflow order**

Recommended final Ares shape:

```python
SequentialAgent(
    name="ares_workflow",
    sub_agents=[
        ares_planning_parallel,
        ares_refinement_loop,
        ares_assembler,
    ],
)
```

If the assembler must run before verification for structural reasons, that is also acceptable. The key is that a real verification loop exists.

- [ ] **Step 6: Commit**

```bash
git add agents/ares_verifier.py agents/ares_reviser.py agents/ares_workflow.py
git commit -m "feat: add LoopAgent-based self-correction to Ares"
```

---

## Task 4: Add One Remote A2A Specialist Agent

**Files:**
- Create: `adk_apps/impact_agent/__init__.py`, `adk_apps/impact_agent/agent.py`
- Create: `agents/impact_agent.py`
- Modify: `agents/zeus.py`
- Modify: `sandbox/models.py` (optional) if a new dashboard-visible agent name is required

Python A2A support is officially available in ADK, but it is experimental. Keep the design small and legible: one remote specialist, one clear handshake, one clear value-add.

### Recommended specialist

**Critical Infrastructure Impact Agent**

Purpose:
- translate cyber evidence into operational consequences
- tell the analyst what physical or service continuity risk exists
- make the project feel bigger than "malware analysis"

Recommended output:
- systems at risk
- outage / continuity implications
- priority actions for operators
- justification tied back to Pantheon evidence

- [ ] **Step 1: Create the specialist agent**

The remote specialist should be narrowly scoped. It should not redo malware analysis. It should consume structured context from Pantheon and produce mission-impact reasoning.

Good prompt shape:
- "You are a critical infrastructure continuity specialist."
- "You do not identify malware families."
- "You assess service continuity risk, outage risk, and operator actions."

- [ ] **Step 2: Expose it as its own ADK app**

`adk_apps/impact_agent/agent.py` should export its own `root_agent`.

Deploy it separately from Pantheon if possible. This makes the handshake materially stronger for judges.

- [ ] **Step 3: Consume it from Pantheon via A2A**

Follow the official ADK A2A consuming quickstart for the exact client / remote-agent wiring supported by the installed version.

Do this **after Apollo** and **before final Zeus synthesis**:
- Hades/Apollo establish evidence
- remote impact specialist translates that into continuity consequences
- Zeus combines cyber + operational guidance

- [ ] **Step 4: Make the handshake visible**

At minimum:
- emit a `HANDOFF` event with `payload={"from": "apollo", "to": "impact_agent", "protocol": "a2a"}`
- emit another handoff or completion event when the response returns

If dashboard node support is needed, add one new `AgentName` enum value and render it as an external specialist node.

- [ ] **Step 5: Commit**

```bash
git add adk_apps/impact_agent/__init__.py adk_apps/impact_agent/agent.py \
  agents/impact_agent.py agents/zeus.py sandbox/models.py
git commit -m "feat: add remote A2A impact specialist for infrastructure continuity"
```

---

## Task 5: Stretch — Wrap `Hades` in a `ParallelAgent`

**Files:**
- Create: `agents/hades_workflow.py`
- Modify: `agents/zeus.py`

This is a good addition, but it is a worse first target than Ares because Hades already has more tool complexity and more error modes.

Recommended fanout:
- branch 1: sandbox analysis (`submit_sample`, `poll_report`, `get_report`)
- branch 2: Windows VPS detonation (`detonate_sample`)
- merger: correlate static/dynamic/VPS evidence and emit attack stages

- [ ] **Step 1: Create two branch specialists**
- [ ] **Step 2: Add a merger agent**
- [ ] **Step 3: Wrap them in `ParallelAgent`**
- [ ] **Step 4: Ensure failures in the VPS branch degrade gracefully**
- [ ] **Step 5: Commit**

Do this only after Tasks 1-4 are working.

---

## Task 6: Stretch — Add an Apollo Evidence Loop

**Files:**
- Create: `agents/apollo_verifier.py`, `agents/apollo_reviser.py`, `agents/apollo_workflow.py`

This is lower ROI than the Ares loop because it is less visually compelling to judges, but it still strengthens the "autonomy over automation" story.

Verifier questions:
- which IOC claims are directly observed vs inferred?
- which enrichment claims are unsupported?
- did Gemini over-attribute a threat actor or campaign?

- [ ] **Step 1: Create Apollo critic**
- [ ] **Step 2: Create Apollo reviser**
- [ ] **Step 3: Wrap in `LoopAgent`**
- [ ] **Step 4: Commit**

---

## Task 7: Deploy the ADK Runtime to Cloud Run

**Files:**
- Modify: `README.md`
- Modify: deployment scripts / Cloud Run config as needed

This is required if you want the Google judges to score deployment and Dev UI visibility highly.

- [ ] **Step 1: Deploy the Pantheon ADK app service to Cloud Run**

The service should:
- serve the ADK web UI
- serve the agent API
- be reachable from a public Google Cloud URL

- [ ] **Step 2: If possible, deploy the remote impact agent as a second Cloud Run service**

This is the cleanest A2A story:
- Pantheon Cloud Run URL
- Impact Specialist Cloud Run URL
- Pantheon consumes the specialist remotely

- [ ] **Step 3: Preserve the existing sandbox deployment separately**

Do not move malware execution to Cloud Run if it complicates containment. The ADK service and the sandbox service can remain distinct.

- [ ] **Step 4: Verify judge-facing URLs**

Must have:
- Pantheon ADK UI URL
- Pantheon API URL
- remote impact agent URL (if separate)

- [ ] **Step 5: Commit docs/config**

```bash
git add README.md infra/
git commit -m "docs: add Google Cloud ADK deployment and demo runbook"
```

---

## Task 8: Make the ADK Work Visible in the Custom Dashboard

**Files:**
- Modify: `frontend/` (Sai)

The ADK Dev UI is mandatory for Google visibility, but the custom dashboard can reinforce the same story.

Recommended UI additions:
- show Ares parallel branches distinctly
- show loop iteration badges in the event feed
- show the remote impact specialist as an external node
- annotate A2A handoffs differently from local sub-agent handoffs

Do **not** redesign the dashboard from scratch. Only add the minimum visibility features needed to make the workflow agents and remote handshake unmistakable.

---

## Task 9: Demo Verification Script

The final judge flow should show all four Google scoring categories in under four minutes.

- [ ] **Step 1: Start with the ADK Dev UI already open**
- [ ] **Step 2: Trigger Pantheon with a real sample**
- [ ] **Step 3: Point out the parallel Ares branches**
- [ ] **Step 4: Point out the verifier loop iteration**
- [ ] **Step 5: Point out the remote A2A specialist handshake**
- [ ] **Step 6: Show the final cyber + operational continuity answer**
- [ ] **Step 7: End with the public Google Cloud URL**

If time is short, the spoken framing should be:

1. "Pantheon is not a chatbot. It is a workforce of specialists."
2. "These three planners are running in parallel because incident response planning splits naturally."
3. "This verifier loop catches unsupported claims and forces a correction pass."
4. "When Pantheon reaches the edge of its expertise, it calls a remote continuity specialist via A2A."
5. "Everything you're seeing is live in the ADK UI on a public Google Cloud deployment."

---

## Recommended Build Order

If the team has limited time, implement in this order:

1. ADK runtime surface + Dev UI
2. `Ares` `ParallelAgent`
3. `Ares` `LoopAgent`
4. One remote A2A impact specialist
5. Cloud Run deployment
6. `Hades` parallel fanout (only if the above is already working)
7. `Apollo` evidence loop (last)

---

## Acceptance Criteria

Pantheon is "Google-track ready" when all of the following are true:

- The judges can open a public Google Cloud URL and see the ADK UI.
- The Pantheon root agent is exposed through the ADK runtime, not just described in docs.
- At least one workflow is implemented with `ParallelAgent`, and the parallelism is legible.
- At least one workflow is implemented with `LoopAgent`, and a retry / self-correction path is legible.
- Pantheon performs one real A2A handshake with a remote specialist.
- The result of the remote specialist materially changes the final answer.
- The malware pipeline still works end-to-end and still answers the three NextEra questions.

---

## References

- ADK overview: https://google.github.io/adk-docs/get-started/about/
- ADK A2A docs: https://google.github.io/adk-docs/a2a/
- ADK Cloud Run deployment + UI: https://google.github.io/adk-docs/deploy/cloud-run/

