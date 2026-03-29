# Infrastructure

This folder defines containerization, service composition, reverse proxy routing, and deployment scripts for Pantheon.

## Files

- `docker-compose.yml`: primary service topology — 3 services on a shared bridge network
- `Dockerfile.sandbox`: build recipe for Hephaestus sandbox API
- `Dockerfile.frontend`: build recipe for Next.js dashboard (multi-stage build)
- `Dockerfile.agents`: build recipe for agent service
- `Dockerfile.gateway`: build recipe for Telegram/voice gateway
- `nginx.conf`: reverse proxy routes (dashboard, WebSocket, sandbox API)
- `deploy.sh`: server deployment helper for `/opt/pantheon`
- `deploy-vultr.sh`: remote deployment orchestrator (SSH to Vultr VPS)
- `deploy-demo.sh`: single-command demo deployment (wraps deploy-vultr.sh)
- `cloud-deploy.sh`: Google Cloud Run deployment (ADK Dev UI + A2A impact agent)

## Docker Compose Services

All three services are active in `docker-compose.yml`:

| Service | Port | Description |
| --- | --- | --- |
| `sandbox` | 9000 | Hephaestus API — analysis, memory, WebSocket events |
| `frontend` | 3000 | Next.js dashboard — landing page + live analysis views |
| `nginx` | 80 | Reverse proxy — routes `/ws`, `/events`, `/sandbox/*` to sandbox; everything else to frontend |

## Nginx Routing

| Path | Target |
| --- | --- |
| `/ws` | `sandbox:9000/ws` (WebSocket upgrade) |
| `/events` | `sandbox:9000/events` |
| `/sandbox/*` | `sandbox:9000` |
| `/` and all other paths | `frontend:3000` |

## Persistent Data

- `samples` volume: sample files and analysis artifacts
- `db` volume: SQLite database (`pantheon.db`)

## Deployment Options

### 1. Vultr VPS (Primary — demo and production)

**From your local machine (one command):**

```bash
./infra/deploy-demo.sh --identity ~/.ssh/id_rsa --copy-env --set-webhook
```

`deploy-demo.sh` orchestrates: `deploy-vultr.sh` → SSH → `deploy.sh` on server.

**Or step-by-step:**

```bash
# Remote deploy via SSH
./infra/deploy-vultr.sh --identity ~/.ssh/id_rsa --copy-env --set-webhook

# Or directly on the server
./infra/deploy.sh --branch master --set-webhook
```

`deploy.sh` flow:
1. Pull latest branch
2. Validate `.env`
3. Build containers
4. Start services
5. Wait for sandbox health check
6. Optionally set Telegram webhook

`--set-webhook` requires `WEBAPP_BASE_URL` and `TELEGRAM_BOT_TOKEN` in `.env` and configures Telegram to post to `${WEBAPP_BASE_URL}/telegram`.

### 2. Google Cloud Run (ADK Demo)

```bash
export GCP_PROJECT_ID=your-project-id
./infra/cloud-deploy.sh
```

Deploys the Pantheon agent tree and remote impact specialist to Cloud Run with ADK Dev UI enabled. Public URLs are printed at the end.

## Operational Commands

```bash
# Build all services
docker compose -f infra/docker-compose.yml build

# Start all services (detached)
docker compose -f infra/docker-compose.yml up -d

# Check service health
docker compose -f infra/docker-compose.yml ps

# View logs
docker compose -f infra/docker-compose.yml logs -f sandbox
docker compose -f infra/docker-compose.yml logs -f frontend
docker compose -f infra/docker-compose.yml logs -f nginx
```

## Security Notes

- Never embed secrets in compose or Dockerfiles; use `.env`.
- Follow malware-safety boundaries in `../CLAUDE.md`.
- Keep outbound restrictions and VPS isolation in place for live detonation workflows.
- The Docker socket is mounted into the sandbox container for container-in-container dynamic analysis.
