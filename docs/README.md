# Documentation

This folder is the source of truth for project design, hackathon strategy, demo scripting, and malware-analysis writeups.

## What Lives Here

| File | Description |
| --- | --- |
| `HACKATHON.md` | Deadlines, judging constraints, submission checklist |
| `demo-judge-walkthrough.md` | 4-minute judge demo script — ADK Dev UI, ParallelAgent, LoopAgent, A2A |
| `team-update-2026-03-28.md` | Team status snapshot |
| `malware-analysis-6108674530.md` | Challenge-specific malware analysis narrative |
| `superpowers/` | Architecture and implementation specs |

### Specs (in `superpowers/specs/`)

- `2026-03-28-pantheon-design.md` — original system architecture
- `2026-03-28-pantheon-dashboard-design.md` — dashboard + event system implementation spec

## Recommended Reading Order

1. `../CLAUDE.md` — safety requirements, architecture boundaries, and team ownership
2. `superpowers/specs/2026-03-28-pantheon-design.md` — baseline system design
3. `superpowers/specs/2026-03-28-pantheon-dashboard-design.md` — event/dashboard implementation
4. `demo-judge-walkthrough.md` — 4-minute judge demo script
5. Hackathon and team update docs for execution planning

## Documentation Standards

- Keep docs decision-oriented: include intent, constraints, and tradeoffs.
- For architecture changes, update specs before or with code changes.
- Prefer adding new dated notes over rewriting historical context.
- Keep malware handling instructions aligned with `../CLAUDE.md` safety rules.

## When Updating The Main README

Use this folder as canonical source material for:

- Product narrative and challenge framing
- Architecture diagrams and service boundaries
- Demo flow and judging-focused positioning
- Key phrases for ADK/A2A/ParallelAgent/LoopAgent scoring categories
