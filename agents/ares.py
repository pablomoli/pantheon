"""Ares — Containment, Remediation, and Prevention agent.

Ares is the final agent in the Pantheon pipeline. It receives the enriched
threat analysis from Apollo and generates three concrete response plans:

1. **Containment** — immediate steps to stop the threat (network isolation,
   process kills, firewall rules, account lockouts).
2. **Remediation** — full eradication steps (file removal, registry cleanup,
   credential rotation, patching).
3. **Prevention** — long-term controls to prevent recurrence (EDR tuning,
   YARA/Sigma rules, network segmentation, monitoring improvements).

Owner: Andres
"""

from __future__ import annotations

from google.adk.agents import Agent

from agents.model_config import ARES_MODEL
from agents.tools.memory_tools import (
    load_prior_runs,
    store_agent_output,
    synthesize_prior_runs,
)
from agents.tools.remediation_tools import (
    build_full_response,
    extract_threat_summary_for_ares,
    generate_containment_plan,
    generate_prevention_plan,
    generate_remediation_plan,
)

_INSTRUCTION = """\
You are Ares, the god of war — Pantheon's containment and remediation specialist.

You receive a fully analysed malware threat. Your job is to respond decisively
with three structured plans that a security team can act on immediately.

## Your Workflow

1. Call `load_prior_runs` with the job_id and agent_name "ares" to check for
   prior Ares plans on this job.
   - If 2 or more prior runs exist, call `synthesize_prior_runs` to get the
     consensus plan. Use it as your starting point — extend and improve it.
   - If 1 prior run exists, review it and build on it rather than repeat it.
2. Call `extract_threat_summary_for_ares` with the threat_report dict and the
   enrichment string that Apollo passed to you in context.
3. Call `generate_containment_plan` with the summary — get immediate actions.
4. Call `generate_remediation_plan` with the summary — get eradication steps.
5. Call `generate_prevention_plan` with the summary — get long-term controls.
6. Call `build_full_response` to assemble the complete incident report from all
   previous agent outputs (threat_report_md, enrichment, containment, remediation,
   prevention).
7. Call `store_agent_output` with the job_id, agent_name "ares", the full
   assembled incident report, and temperature 0.3. This enables synthesis on
   future runs.
8. Return the assembled markdown document as your final response.

## Rules

- Never skip any of the three plans, even for low-risk samples.
- Be specific and technical — generic advice is not acceptable.
- Reference actual IOCs (IPs, domains, file paths, registry keys) in your plans.
- Use [CRITICAL], [HIGH], or [MEDIUM] urgency labels on containment steps.
"""

ares: Agent = Agent(
    name="ares",
    model=ARES_MODEL,
    description=(
        "Containment, remediation, and prevention specialist. "
        "Generates three actionable response plans from a completed threat analysis."
    ),
    instruction=_INSTRUCTION,
    tools=[
        extract_threat_summary_for_ares,
        generate_containment_plan,
        generate_remediation_plan,
        generate_prevention_plan,
        build_full_response,
        load_prior_runs,
        store_agent_output,
        synthesize_prior_runs,
    ],
)
