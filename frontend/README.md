# Frontend Dashboard

This is the real-time Pantheon dashboard built with Next.js, Tailwind, and React Flow.

It visualizes the malware-analysis swarm by consuming the live event stream from Hephaestus (`/ws`) and rendering:

- agent activation/completion states
- inter-agent handoffs
- tool activity
- attack-chain progression
- process and IOC telemetry

## Core Architecture

The dashboard follows an event-first model.

1. WebSocket client receives `PantheonEvent` messages from sandbox.
2. Events are normalized and stored in a shared state store.
3. UI components subscribe to slices of state and render live updates.

No dashboard panel should rely on polling REST snapshots as primary source of truth.

## Important Paths

- `src/lib/pantheon-ws.ts`: WebSocket connection and event ingestion
- `src/lib/event-store.ts`: shared event-driven state
- `src/components/`: dashboard visual components (graph, feed, attack chain, IOC views)
- `src/app/`: Next.js app routes/pages

Additional notes are in:

- `README_DASHBOARD.md`
- `SETUP.md`

## Environment

Set sandbox endpoint for local/prod:

- `SANDBOX_API_URL`

Examples:

- local: `http://localhost:9000`
- production: your deployed sandbox base URL

## Local Development

From this folder:

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Build And Validate

```bash
npm run lint
npm run build
```

## Dashboard Implementation Goals

- Keep all major panels wired to event-store state.
- Make node and edge transitions reflect real event timing.
- Keep event feed readable under high event volume.
- Ensure layout remains usable on desktop and mobile.

## Integration Contract

The event schema is defined by backend Pydantic models in `../sandbox/models.py`.

When backend event shapes change:

1. update parsing in `src/lib/pantheon-ws.ts`
2. update state transforms in `src/lib/event-store.ts`
3. adjust component renderers accordingly
