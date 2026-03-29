# Documentation

This folder is the source of truth for project design, hackathon strategy, and malware-analysis writeups.

## What Lives Here

- `HACKATHON.md`: deadlines, judging constraints, and submission checklist
- `team-update-2026-03-28.md`: team status snapshot
- `malware-analysis-6108674530.md`: challenge-specific analysis narrative
- `superpowers/`: architecture and implementation specs (including dashboard/event system)

## Recommended Reading Order

1. `../CLAUDE.md` for safety requirements and architecture boundaries
2. `superpowers/specs/2026-03-28-pantheon-design.md` for baseline system design
3. `superpowers/specs/2026-03-28-pantheon-dashboard-design.md` for event/dashboard implementation
4. Hackathon and team update docs for execution planning

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
