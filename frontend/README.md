# Frontend Dashboard

The real-time Pantheon dashboard built with **Next.js**, **Tailwind CSS**, and **React Flow**.

It visualizes the malware-analysis swarm by consuming the live event stream from Hephaestus (`/ws`) and rendering agent activity, attack-chain progression, IOC telemetry, and process-level observations — all in real time.

## Routes

| Path | Description |
| --- | --- |
| `/` | Landing page — Greek-themed with laurel wreaths, columns, and agent spotlight cards |
| `/dashboard` | Live analysis dashboard — the primary operational view |
| `/olympus` | OlympusFlow — React Flow agent graph with animated nodes and edges |
| `/trace` | TraceViewer — ADK execution timeline playback |

## Core Architecture

The dashboard follows an **event-first** model:

1. WebSocket client (`pantheon-ws.ts`) connects to `ws://<SANDBOX_URL>/ws` and receives `PantheonEvent` messages.
2. Events are normalized and stored in a shared Zustand-style state store (`event-store.ts`).
3. UI components subscribe to slices of state and render live updates.

No dashboard panel should rely on polling REST endpoints as the primary source of truth.

## Key Files

- `src/lib/pantheon-ws.ts`: WebSocket connection, auto-reconnect, event deserialization
- `src/lib/event-store.ts`: shared event-driven state — active agents, event feed, attack chain, IOCs, process tree
- `src/components/`: all dashboard visual components (21 components)
- `src/app/`: Next.js app routes and pages

### Component Inventory

| Component | Purpose |
| --- | --- |
| `PantheonDashboard.tsx` | Main dashboard container — manages layout, event store, and WebSocket lifecycle |
| `OlympusFlow.tsx` | React Flow agent graph — 8+ nodes with pulse/glow on active, edge animation on handoff |
| `DivineChronicle.tsx` | Event feed — auto-scroll, color-coded by event type, expandable tool calls |
| `AttackChain.tsx` | Horizontal stage cards — populated from STAGE_UNLOCKED events |
| `AgentInspector.tsx` | Per-agent telemetry panel — tool call history, latency metrics |
| `AgentPipeline.tsx` | Pipeline visualization of agent handoff sequence |
| `TraceViewer.tsx` | ADK execution timeline — ParallelAgent and LoopAgent rendering |
| `VoiceChat.tsx` | Voice interaction panel — Muse/ElevenLabs integration |
| `AgentGraph.tsx` | Simplified agent relationship graph |
| `AgentGrid.tsx` | 2×3 agent card grid with status indicators |
| `ActivityStream.tsx` | Scrollable event log (newest first) |
| `EventFeed.tsx` | Generic event feed renderer |
| `GodCard.tsx` | Individual agent card with identity, role, and status |
| `HUDBar.tsx` | Top bar — connection status, active agent count, event counter |
| `IOCPanel.tsx` | IOC sidebar — severity-filtered indicators |
| `IOCTracker.tsx` | Extended IOC tracking with search and filtering |
| `JobOverview.tsx` | Job metadata card — ID, status, timestamps, event count |
| `SlidePanel.tsx` | Slide-out detail panel |
| `TelemetryStream.tsx` | Process/network telemetry visualization |
| `ProfessionalDashboard.tsx` | Alternative clean layout |
| `UltraDashboard.tsx` | Full-featured dashboard variant |

### Additional Documentation

- `README_DASHBOARD.md` — design philosophy and component architecture
- `SETUP.md` — step-by-step local setup with troubleshooting guide

## Environment

Set the sandbox endpoint in `frontend/.env.local`:

```bash
NEXT_PUBLIC_SANDBOX_URL=http://localhost:9000          # local development
NEXT_PUBLIC_SANDBOX_URL=http://155.138.218.106:9000    # production (Vultr)
```

## Local Development

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 (landing) or http://localhost:3000/dashboard (live dashboard).

## Build and Validate

```bash
npm run lint
npm run build
```

## Integration Contract

The event schema is defined by backend Pydantic models in `../sandbox/models.py`.

When backend event shapes change:

1. Update parsing in `src/lib/pantheon-ws.ts`
2. Update state transforms in `src/lib/event-store.ts`
3. Adjust component renderers accordingly
