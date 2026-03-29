# Pantheon - Google ADK Workflow + A2A Design

**Date:** 2026-03-28
**Status:** Proposed - implementation target for Google ADK challenge push
**Authors:** Pantheon team

---

## 1. Overview

This document defines the Google Cloud ADK-specific evolution of Pantheon.

Pantheon already has a strong specialist-agent story for malware analysis and
incident response:

- Zeus orchestrates the pipeline
- Athena triages the incident
- Hades analyzes the malware
- Apollo extracts and enriches IOCs
- Ares generates containment, remediation, and prevention guidance

That is enough to qualify as a multi-agent system, but it is not yet the
strongest possible submission for the Google ADK challenge. In its current
form, Pantheon is primarily a sequential specialist pipeline with a custom
dashboard.

To maximize competitiveness for the Google judging rubric, Pantheon needs four
additional properties:

1. A visible ADK runtime surface with Dev UI and public URL
2. At least one real `ParallelAgent` workflow where parallelism improves the result
3. At least one real `LoopAgent` workflow where the system self-corrects
4. At least one visible A2A handshake with a remote specialist agent

This design introduces those capabilities without breaking the core NextEra
malware-analysis demo.

---

## 2. Problem Statement

The Google challenge is not rewarding "an app with multiple prompts." It is
rewarding a distributed workforce of agents that can observe, reason, and act
with visible autonomy.

Pantheon already does the following well:

- calls real tools
- analyzes a real malicious sample
- persists memory and prior runs
- emits real-time events to a live dashboard
- produces actionable containment and remediation output

Pantheon is currently weaker on the following Google-specific dimensions:

- no public ADK UI surface
- no explicit workflow-agent primitives
- no loop-driven self-correction
- no remote A2A specialist handshake
- no strong judge-visible "trace" inside the official ADK runtime

This design closes those gaps.

---

## 3. Design Goals

### 3.1 Primary goals

1. Preserve Pantheon's real malware-analysis and response pipeline
2. Add unmistakable ADK-native workflow sophistication
3. Make the workflow legible to judges in under four minutes
4. Expand the story from "malware analyzer" to "critical infrastructure resilience system"

### 3.2 Secondary goals

1. Reuse existing specialist agents instead of rewriting them
2. Keep the change set small enough to finish before demo time
3. Make the Google-track additions reinforce, not distract from, the NextEra pitch

### 3.3 Non-goals

1. Replacing all existing agents with workflow agents
2. Building a large multi-remote-agent network
3. Moving the sandbox runtime into Cloud Run if it complicates containment
4. Adding "fake" loops or "fake" parallelism just to satisfy the rubric

---

## 4. Design Principles

### 4.1 Keep specialist agents as the brains

Zeus, Athena, Hades, Apollo, and Ares remain domain-specific specialists. The
new workflow agents orchestrate them; they do not replace their expertise.

### 4.2 Add workflow primitives only where the workflow is real

`ParallelAgent` should only be used when the branches are materially
independent. `LoopAgent` should only be used when the system can evaluate its
own output and improve it.

### 4.3 Optimize for visibility, not just correctness

The Google judges need to see the branching, looping, and A2A handshake
directly in the ADK trace. Invisible sophistication does not score well.

### 4.4 Preserve actionability

Pantheon must remain a system that actually does things:

- calls the sandbox
- calls the Windows VPS
- stores memory
- emits events
- produces operator guidance

The ADK additions must amplify that, not abstract it away.

---

## 5. Updated System Architecture

### 5.1 Current architecture

```text
User
  -> Zeus
     -> Athena
     -> Hades
     -> Apollo
     -> Ares
  -> final response

Hephaestus EventBus -> custom dashboard
```

### 5.2 Target architecture

```text
User
  -> Zeus (LlmAgent)
     -> Athena (LlmAgent)
     -> Hades (LlmAgent)
     -> Apollo (LlmAgent)
     -> Impact Specialist (remote A2A agent)
     -> AresWorkflow (workflow wrapper)
        -> AresPlanningParallel (ParallelAgent)
           -> ContainmentPlanner
           -> RemediationPlanner
           -> PreventionPlanner
        -> AresRefinementLoop (LoopAgent)
           -> AresVerifier
           -> AresReviser
        -> AresAssembler
  -> final response

ADK Dev UI + Hephaestus EventBus dashboard run side-by-side
```

### 5.3 Why Ares is the first workflow target

Ares is the cleanest workflow migration because:

- containment planning is independent from remediation planning
- prevention planning is independent from both
- all three are fed by the same threat summary
- the output is already naturally assembled into one final report

This gives Pantheon a very visible `ParallelAgent` use case with low risk.

---

## 6. ADK Runtime Surface

Pantheon must expose a real ADK runtime surface backed by the official FastAPI
integration so judges can use the ADK Dev UI.

### 6.1 ADK app structure

Pantheon should add one ADK-discoverable app folder for the root agent and one
for the remote impact specialist.

Recommended structure:

```text
adk_apps/
  pantheon_agent/
    __init__.py
    agent.py          # exports root_agent = zeus (or a thin root wrapper)
  impact_agent/
    __init__.py
    agent.py          # exports root_agent for remote specialist
```

### 6.2 ADK server

Pantheon should add a FastAPI entrypoint that uses ADK's `get_fast_api_app()`
with `web=True` so the UI is served directly.

This server should become the runtime surface for:

- ADK web UI
- session creation and persistence
- API-based testing
- public Google Cloud deployment

### 6.3 Why this matters

Without an ADK runtime surface, Pantheon is only *described* as an ADK system.
With it, judges can directly inspect:

- sessions
- branches
- loops
- tool traces
- remote-agent interactions

---

## 7. Workflow-Agent Strategy

### 7.1 Keep Zeus as an LLM orchestrator

Zeus remains the top-level LLM agent because the root orchestration task is
dynamic and judgment-heavy. It is not a good candidate for deterministic
workflow control.

### 7.2 Keep Athena as a simple specialist

Athena is intentionally lightweight. Converting it to a workflow agent would
add complexity without improving the score.

### 7.3 Ares becomes a workflow-backed planning system

The recommended Ares design is:

```text
AresWorkflow (SequentialAgent)
  -> AresPlanningParallel (ParallelAgent)
     -> AresContainmentPlanner
     -> AresRemediationPlanner
     -> AresPreventionPlanner
  -> AresRefinementLoop (LoopAgent)
     -> AresVerifier
     -> AresReviser
  -> AresAssembler
```

This gives Pantheon:

- one visible parallel fanout
- one visible self-correction loop
- one final assembled artifact

### 7.4 Stretch: Hades parallel fanout

Hades can also be wrapped later:

```text
HadesWorkflow (SequentialAgent)
  -> HadesAnalysisParallel (ParallelAgent)
     -> HephaestusBranch
     -> WindowsVpsBranch
  -> HadesMerger
```

This is a valid use of `ParallelAgent`, but it is more operationally risky than
the Ares migration because the Hades branches touch more external systems and
error conditions.

### 7.5 Stretch: Apollo evidence loop

Apollo can later gain a verifier loop:

```text
ApolloWorkflow (SequentialAgent)
  -> ApolloDraft
  -> ApolloEvidenceLoop (LoopAgent)
     -> ApolloVerifier
     -> ApolloReviser
```

This helps the "hallucination resistance" story, but it is less visible than
the Ares loop and should not be the first workflow migration.

---

## 8. Ares Parallel Workflow Design

### 8.1 Inputs

The Ares workflow consumes:

- formatted threat report from Apollo
- threat-intel enrichment from Apollo
- underlying threat summary / IOC context
- job ID for persistence and event emission

### 8.2 Parallel branches

The three branches are:

1. Containment planner
2. Remediation planner
3. Prevention planner

Each branch should:

- receive the same threat summary
- call only the tools relevant to its domain
- write its output to a stable state key
- emit events that identify the workflow and branch

### 8.3 Assembler

The assembler should:

- read all three plan outputs
- call `build_full_response`
- store the assembled report
- return the final artifact back up the chain

### 8.4 Judge-visible value

This parallel fanout is easy to explain:

"Incident response planning splits into three independent workstreams. Pantheon
runs them at once instead of waiting for one to finish before starting the next."

That is materially stronger than simply saying "we have multiple agents."

---

## 9. Ares Self-Correction Loop Design

### 9.1 Verifier responsibilities

The verifier checks whether the generated plans are:

- evidence-backed
- operationally specific
- free from invented IOCs or unsupported claims
- complete across containment, remediation, and prevention

The verifier is not allowed to invent new evidence. It can only approve,
reject, or request revision.

### 9.2 Reviser responsibilities

The reviser reads:

- the current Ares response
- verifier findings
- underlying evidence from Apollo / Hades

It then produces a corrected response that tightens claims, removes unsupported
details, and increases specificity.

### 9.3 Loop termination

The loop should have a small hard cap, ideally `max_iterations=2`.

Pantheon does not need an open-ended loop. Judges only need to see:

- one verification pass
- either one revision or one approval

### 9.4 Judge-visible value

This is the strongest answer to the "autonomy over automation" requirement:

"Pantheon does not trust its first draft. It critiques its own response and
revises it before returning a final operator plan."

---

## 10. Remote A2A Specialist Design

### 10.1 Specialist role

The recommended remote specialist is a **Critical Infrastructure Impact Agent**.

Its job is not to repeat malware analysis. Its job is to translate cyber
evidence into continuity and operational consequences.

Examples:

- what plant, field, or operator systems are at risk
- what outage or service continuity consequences could follow
- what an operator should do in the next 15 minutes

### 10.2 Why this specialist is the right fit

This specialist improves two separate axes of the Google rubric:

1. **A2A interoperability**
   Pantheon clearly reaches outside its own skill boundary.

2. **Social impact / moonshot framing**
   The project becomes about infrastructure resilience and service continuity,
   not just malware reverse engineering.

### 10.3 Invocation point

The remote specialist should be called after Apollo has produced evidence and
before Zeus synthesizes the final answer.

Recommended order:

```text
Athena -> Hades -> Apollo -> remote impact specialist -> AresWorkflow -> Zeus summary
```

This keeps the remote specialist focused on interpretation, not raw detection.

### 10.4 A2A deployment model

The ideal configuration is two separate services:

- Pantheon ADK service
- Impact Specialist ADK service

Pantheon consumes the remote service through A2A. This is much more convincing
to judges than keeping both specialists inside one local hierarchy.

---

## 11. State, Eventing, and Traceability

Pantheon already has a strong custom event stream. The new ADK workflows should
reuse that infrastructure rather than inventing a second custom tracing system.

### 11.1 Event recommendations

Keep the existing event schema and enrich payloads with workflow metadata:

- `workflow`: which workflow wrapper emitted the event
- `branch`: which parallel branch is active
- `iteration`: current loop iteration if applicable
- `protocol`: `"a2a"` for remote handoffs

### 11.2 Custom dashboard role

The custom dashboard remains useful for:

- event feed
- attack-chain visualization
- sandbox/VPS visibility
- process / IOC tree

### 11.3 ADK Dev UI role

The ADK Dev UI becomes the canonical judge-facing view for:

- workflow branching
- loop iterations
- session trace
- remote-agent interactions

Pantheon should show both.

---

## 12. Deployment Model

### 12.1 Public Google Cloud URL

To score well on deployment and Googliness, Pantheon should expose the ADK app
through a public Google Cloud URL, ideally Cloud Run.

### 12.2 Split runtime model

Recommended deployment split:

- **Cloud Run / ADK service**
  Hosts the Pantheon ADK app and optionally the remote impact specialist

- **Existing sandbox service**
  Continues to host Hephaestus and the malware-analysis backend

This preserves safety and keeps the ADK visibility layer separate from the
sandbox execution layer.

### 12.3 Public surfaces

Pantheon should be able to present:

- public ADK UI URL
- public ADK API URL
- remote impact specialist URL if deployed separately

---

## 13. Demo Flow

The Google-track demo should be optimized for clarity and speed.

Recommended sequence:

1. Start with the ADK Dev UI already open
2. Trigger Pantheon with a real suspicious sample
3. Show the normal specialist pipeline activating
4. Highlight the Ares parallel planning fanout
5. Highlight the Ares verifier loop
6. Highlight the remote A2A impact-specialist handshake
7. Show the final response that includes both cyber response and operational continuity guidance
8. End on the public Google Cloud URL

This should be explained as:

"Pantheon is a workforce, not a chatbot. These planning branches run in
parallel, this verifier loop self-corrects unsupported claims, and when
Pantheon reaches the edge of its expertise it calls a remote infrastructure
continuity specialist through A2A."

---

## 14. Judging Criteria Alignment

### 14.1 Architectural sophistication

This design directly answers the rubric:

- `ParallelAgent`: Ares planning fanout
- `LoopAgent`: Ares verification/revision loop
- A2A interoperability: remote impact specialist
- efficiency: incident-response plans produced in parallel instead of serially

### 14.2 Social impact and moonshot vision

The remote specialist shifts Pantheon from "malware analysis" to "critical
infrastructure resilience." That is a much stronger fit for the challenge's
"workforce for good" framing.

### 14.3 Technical rigor and Googliness

The design adds:

- official ADK runtime surface
- ADK Dev UI
- A2A remote specialist
- public Google Cloud deployment

### 14.4 Pitch and trace

Judges will see:

- live ADK workflow trace
- live Pantheon event dashboard
- parallel branches
- self-correction
- remote handshake

That is substantially more legible than a purely custom orchestration story.

---

## 15. Risks and Constraints

### 15.1 Time risk

The team should not attempt every possible workflow migration. The highest-value
minimum set is:

1. ADK runtime surface
2. Ares parallel planning
3. Ares self-correction loop
4. one remote A2A specialist

### 15.2 Experimental A2A support

Python A2A support is experimental. That makes it a good demo target, but the
scope must remain small and controlled.

### 15.3 Demo stability

The NextEra malware-analysis path is the primary demo. The Google additions must
not destabilize the real malware-analysis tool calls or the final response path.

---

## 16. Acceptance Criteria

This design is considered implemented when all of the following are true:

1. Pantheon is exposed through a working ADK FastAPI runtime with web UI
2. Judges can access a public Google Cloud URL for the ADK service
3. At least one `ParallelAgent` workflow is visible and meaningful
4. At least one `LoopAgent` workflow is visible and meaningful
5. Pantheon performs one real remote A2A handshake
6. The remote specialist materially contributes to the final response
7. The original malware-analysis and incident-response pipeline still works end-to-end

---

## 17. Recommended Implementation Order

1. Add the ADK runtime surface and Dev UI
2. Implement Ares parallel planning
3. Implement Ares verification loop
4. Add the remote A2A impact specialist
5. Deploy to Cloud Run
6. Add optional Hades parallelism
7. Add optional Apollo evidence loop

---

## 18. What This Unlocks for Judges

With this design, Pantheon becomes easy to score highly as a Google ADK
submission because the judges can watch all four of the important ideas happen
live:

- specialization
- parallelism
- self-correction
- remote collaboration

The result is no longer just "an AI malware analyzer." It is a visible,
autonomous cyber-resilience workforce.

