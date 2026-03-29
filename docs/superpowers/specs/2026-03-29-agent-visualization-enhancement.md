# Agent Visualization Enhancement — Pantheon Dashboard

**Date:** 2026-03-29
**Scope:** `/dashboard` route only — `OlympusFlow`, `ProfessionalDashboard`, `AgentInspector`, `DivineChronicle`, `IOCPanel`
**Goal:** Make the agent graph the dominant, visually striking element of the dashboard while preserving the existing cream/gold color palette.

---

## 1. Layout Restructure

### Current
Three-column grid: `[stats+IOCs col-3] [graph col-6] [inspector col-3]` with a `h-64` event log below.

### New
The main area has two zones:

**Top HUD bar** (48px fixed height, `glass-panel` strip):
- Left: job name + pipeline stage progress — four labeled dots (`Triage → Analysis → Enrichment → Response`) that fill gold as stages complete, derived from `JobState.status`
- Right: three stat counters (active agents, total events, critical IOCs) + WS connection dot

**Graph canvas** (everything below the HUD bar):
- Full width, full remaining height
- `OlympusFlow` fills this space with `fitView` and generous padding

**Collapsed sidebar**:
- Reduced from `w-64` to `w-12` (48px)
- Shows only Lucide icons for the four nav tabs, vertically centered
- Tooltips on hover for labels
- Connection status dot at the bottom
- The "Pantheon" wordmark and descriptive text are removed from the sidebar; the top HUD serves as the header

**Secondary panels** (IOC list, event log, agent inspector) are removed from the persistent layout and become slide-in drawers. Three trigger buttons are anchored to the right edge of the HUD bar:
- `List` icon → IOC drawer (slides in from right, 360px wide)
- `Radio` icon → Event log drawer (slides in from right, 360px wide)
- These drawers overlay the graph with a semi-transparent linen backdrop and a close button

---

## 2. Graph Node Redesign (`GodNode`)

### Size
- Standard agents: 96px diameter circle
- Zeus: 112px diameter circle

### Anatomy (outer to inner)
1. **Glow ring** — a `div` positioned absolutely behind the node circle, same diameter + 24px, rounded-full, `background: radial-gradient` in the agent's color. At rest: 15% opacity. When `state === 'active'`: 60% opacity, `animation: pulse-ring 1.5s ease-in-out infinite` (scale 1.0 → 1.15 → 1.0).
2. **Node circle** — white `glass-panel` circle, `border-2` in the agent's color at rest (30% opacity), border brightens to 100% opacity when active. Drop shadow: `box-shadow: 0 0 32px {color}40` at rest, `0 0 56px {color}80` when active.
3. **Icon** — Lucide icon, 32px, agent color
4. **State dot** — 10px circle, `absolute top-1 right-1`, green when complete, amber+pulse when active, slate when idle, red when error
5. **Label** — agent name below the circle, `text-xs font-bold uppercase tracking-widest`, `color: gold-dark`
6. **Thought line** — `AnimatePresence` fade-in below the label, `text-[10px] italic text-muted max-w-[120px] text-center truncate`, only rendered when `data.last_thought` is set and `state === 'active'`

### Zeus distinction
Zeus gets a second outer ring — a thin gold dashed circle at 140px diameter, always visible at 20% opacity, functioning as a visual "command radius".

---

## 3. Edge Redesign — `ParticleEdge`

A custom ReactFlow edge type replaces the default animated edge.

### Rest state
All Zeus→agent base edges: `strokeDasharray: "4 6"`, `stroke: rgba(201,162,39,0.12)`, `strokeWidth: 1`. These are always present.

### Handoff state
When a `HANDOFF` event fires for a given `from→to` pair, a `ParticleEdge` is rendered for that pair with:
- The edge path brightens: `stroke: {sourceAgentColor}`, `strokeWidth: 2`, `opacity: 0.6`
- 4 particle dots animate along the SVG path using `stroke-dashoffset` animation over 800ms. Each dot is a small circle (`r=3`) following a `motion.circle` along the path using `offsetDistance` CSS animation.
- After `800ms * 1.2` the handoff edge fades back to the rest dashed style

### Implementation
`ParticleEdge` is a React component registered in `nodeTypes` (actually `edgeTypes`). It receives `sourceX/Y`, `targetX/Y`, computes an SVG bezier path (same as ReactFlow's default), renders the base path, and conditionally renders particle elements when `data.active === true`. The `OlympusFlow` parent derives `activeHandoffs` from `store.getHandoffs()` filtered to the last 1200ms and passes this as edge data.

---

## 4. Agent Inspector — Slide-in Overlay

`AgentInspector` is converted from a persistent right column to a fixed overlay panel.

- Position: `fixed right-0 top-0 h-full w-80 z-50`
- Entry animation: `translateX(100%) → translateX(0)` via `framer-motion` `AnimatePresence`
- Backdrop: `fixed inset-0 bg-linen/40 backdrop-blur-sm z-40` (click to dismiss)
- Content: identical to current — header with agent icon/name/role, stats grid, current task, last thought, control buttons
- Triggered by clicking any node in `OlympusFlow`; `onSelect` callback in `ProfessionalDashboard` sets `selectedAgent` state; `null` closes it

---

## 5. Event Log Drawer (`DivineChronicle`)

- Position: `fixed right-0 top-0 h-full w-96 z-50` (same pattern as inspector, triggered separately)
- Entry animation: slide from right
- Content identical to current — event list with type icons, agent labels, timestamps
- Trigger: `Radio` button in HUD bar right cluster

---

## 6. IOC Drawer (`IOCPanel`)

- Same slide-in pattern, `w-96`
- Content identical to current — severity summary, filter tabs, IOC list
- Trigger: `List` button in HUD bar right cluster

---

## 7. CSS Additions (`globals.css`)

```css
@keyframes pulse-ring {
  0%, 100% { transform: scale(1);    opacity: 0.6; }
  50%       { transform: scale(1.15); opacity: 0.3; }
}

@keyframes particle-travel {
  0%   { stroke-dashoffset: 100; }
  100% { stroke-dashoffset: 0;   }
}
```

No new color variables — uses existing `--color-gold`, `--color-gold-dark`, `--color-linen`, `--color-ink`.

---

## 8. Files Changed

| File | Nature of change |
|------|-----------------|
| `ProfessionalDashboard.tsx` | Full layout rework — collapsed sidebar, HUD bar, drawer state management |
| `OlympusFlow.tsx` | `GodNode` redesign, `ParticleEdge` custom edge type, wider radius (320px) |
| `AgentInspector.tsx` | Convert to fixed slide-in overlay, dark backdrop |
| `DivineChronicle.tsx` | Convert to fixed slide-in drawer |
| `IOCPanel.tsx` | Convert to fixed slide-in drawer |
| `globals.css` | Add `pulse-ring` and `particle-travel` keyframes |

`GodCard.tsx`, `PantheonDashboard.tsx` (the `/olympus` demo), `TraceViewer`, and the landing page are untouched.

---

## 9. Out of Scope

- The `/olympus` demo page — separate component, not touched
- The `/trace` page — separate component, not touched
- The landing page — not touched
- Mobile layout — dashboard is desktop-only
- Agent controls (pause/resume/stop) — kept as-is inside the inspector
