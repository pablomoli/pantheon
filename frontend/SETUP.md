# Getting Started — Pantheon Dashboard

## Prerequisites

The dashboard connects to **Hephaestus** (Sandbox API) via WebSocket. You need to:

1. **Install Python 3.12+** (you have 3.11.0, need to upgrade or use 3.12+)
2. **Install uv** (Python package manager)
3. **Start Hephaestus** backend service
4. **Configure frontend** environment
5. **Start frontend** dev server

## Installation Steps

### Step 1: Set Up Backend (One Time)

```bash
# Install uv (macOS)
brew install uv

# Verify installation
uv --version
```

If you don't have Homebrew:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Install Python Dependencies

```bash
cd /Users/sairamen/projects/pantheon

# Install all dependencies (backend + agents + frontend)
uv sync
```

This will read `pyproject.toml` and install:
- google-adk, transformers
- fastapi, uvicorn (Hephaestus server)
- pydantic, httpx
- python-telegram-bot, elevenlabs
- All dev tools (mypy, ruff, pytest)

### Step 3: Start Hephaestus (Backend)

In one terminal:

```bash
cd /Users/sairamen/projects/pantheon
uv run python sandbox/main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:9000
INFO:     Application startup complete
```

Verify it's working:
```bash
curl http://localhost:9000/sandbox/health
# Response: {"status":"healthy"}
```

### Step 4: Configure Frontend

In the frontend directory:

```bash
cd /Users/sairamen/projects/pantheon/frontend

# Set up environment for local development
cat > .env.local << 'EOF'
NEXT_PUBLIC_SANDBOX_URL=http://localhost:9000
EOF
```

### Step 5: Start Frontend

In another terminal:

```bash
cd /Users/sairamen/projects/pantheon/frontend
npm install
npm run dev
```

You should see:
```
  ▲ Next.js 16.2.1 (Turbopack)
  - Local:        http://localhost:3000
  - Dashboard:    http://localhost:3000/dashboard
```

Open: **http://localhost:3000/dashboard**

The dashboard should show **Connected ✓** (green) in top right.

## Architecture

```
Terminal 1                    Terminal 2                    Browser
───────────              ──────────────                  ─────────
uv run python       npm run dev
sandbox/main.py     (Next.js frontend)         http://localhost:3000/dashboard
   ↓                    ↓                           ↓
Hephaestus        Frontend App                  Dashboard UI
:9000             :3000                    (Auto-reconnects to :9000/ws)
 │                 │                         │
 │←────WS/ws───────┼─────────────────────────┤
 │                 │                         │
```

## Status Indicators

### Connected (Green ✓)
- Hephaestus is running and reachable
- WebSocket connection is active
- Ready to receive events/submit samples

### Offline (Amber ⚠️)
- Hephaestus is not running OR
- Wrong URL in `.env.local` OR
- Network connectivity issue

**Fix**: 
1. Check Hephaestus is running in Terminal 1
2. Verify URL: `curl http://localhost:9000/sandbox/health`
3. Verify `.env.local` has `NEXT_PUBLIC_SANDBOX_URL=http://localhost:9000`
4. Frontend will auto-reconnect every 2-10 seconds

## Testing the Connection

### 1. Verify Backend

```bash
# Health check
curl http://localhost:9000/sandbox/health

# WebSocket endpoint exists
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:9000/ws
# Should get 101 Switching Protocols
```

### 2. Check Frontend Console

Open http://localhost:3000/dashboard and check browser DevTools console:

**Expected (connected)**:
```
[Pantheon WS] Configured to connect to: ws://localhost:9000/ws
[Pantheon WS] ✓ Connected to ws://localhost:9000/ws
✓ Connected to Pantheon EventBus
```

**If disconnected**:
```
[Pantheon WS] Configured to connect to: ws://localhost:9000/ws
[Pantheon WS] Attempting connection to ws://localhost:9000/ws...
[Pantheon WS] WebSocket connection failed. Ensure Hephaestus is running...
WebSocket connection error: WebSocket connection timeout...
```

If you see this, make sure Hephaestus is running (should see "Uvicorn running" in Terminal 1).

## Troubleshooting

### "uv: command not found"

Install uv:
```bash
brew install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "ModuleNotFoundError: No module named 'docker'"

Run dependency install:
```bash
cd /Users/sairamen/projects/pantheon
uv sync
```

### "Connection refused" or "Offline" status

**Dashboard shows "Offline" but you want "Connected"?**

1. **Check Terminal 1**: Is Hephaestus running?
   ```bash
   # Terminal 1 should show:
   # INFO:     Uvicorn running on http://0.0.0.0:9000
   ```
   If not, start it:
   ```bash
   cd /Users/sairamen/projects/pantheon
   uv run python sandbox/main.py
   ```

2. **Check frontend URL**: 
   ```bash
   # frontend/.env.local should have:
   NEXT_PUBLIC_SANDBOX_URL=http://localhost:9000
   ```

3. **Restart frontend**:
   ```bash
   # Kill Terminal 2 (npm run dev)
   # Ctrl+C to stop it
   
   # Start again
   npm run dev
   ```

4. **Check console logs**:
   - Open http://localhost:3000/dashboard
   - Open DevTools: F12 or Cmd+Option+I
   - Go to Console tab
   - Look for: `[Pantheon WS] ✓ Connected to ws://localhost:9000/ws`
   - If you see connection errors, Hephaestus isn't running

### "Connection timeout"

The dashboard tries to connect for 5 seconds then gives up. If you see timeout errors:

1. Stop frontend (Ctrl+C in Terminal 2)
2. Start Hephaestus (in Terminal 1)
3. Wait for "Application startup complete" message
4. Restart frontend (Terminal 2)
5. Open dashboard in browser

The auto-reconnect will kick in and connect.

## Quick Start (TL;DR)

```bash
# Terminal 1 — Start Backend
cd /Users/sairamen/projects/pantheon
brew install uv  # if needed
uv sync
uv run python sandbox/main.py
# Wait for: "Application startup complete"

# Terminal 2 — Start Frontend
cd /Users/sairamen/projects/pantheon/frontend
npm install
npm run dev

# Browser
# Open: http://localhost:3000/dashboard
# Should show "Connected ✓" (green) in top right
```

## Command Reference

| Task | Command | Terminal |
|------|---------|----------|
| Install dependencies | `uv sync` | Terminal 1 (once) |
| Start Hephaestus | `uv run python sandbox/main.py` | Terminal 1 |
| Install frontend deps | `npm install` | Terminal 2 (once) |
| Start frontend | `npm run dev` | Terminal 2 |
| Open dashboard | `http://localhost:3000/dashboard` | Browser |
| Check Hephaestus health | `curl http://localhost:9000/sandbox/health` | Terminal 3 |

## Environment Files

**`/Users/sairamen/projects/pantheon/.env`** — Backend configuration (Telegram, API keys, etc.)

**`/Users/sairamen/projects/pantheon/frontend/.env.local`** — Frontend configuration
```
NEXT_PUBLIC_SANDBOX_URL=http://localhost:9000
```

## Next: Testing the System

Once connected:

1. **Monitor the dashboard** — Real-time agent execution and events
2. **Submit a malware sample** — Via Telegram bot (Hermes) or direct upload
3. **Watch agents work in parallel** — Zeus, Athena, Hades, Apollo, Ares
4. **See IOCs discovered** — Live in the Indicators panel
5. **Track events** — Real-time in Activity Stream (click to expand)

Happy hunting! 🔍
