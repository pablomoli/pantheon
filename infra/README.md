# Infrastructure

This folder defines containerization, service composition, reverse proxy behavior, and deployment scripts for Pantheon.

## Files

- `docker-compose.yml`: primary service topology and volumes/networks
- `Dockerfile.sandbox`: build recipe for Hephaestus sandbox API
- `Dockerfile.agents`: build recipe for agent service
- `Dockerfile.gateway`: build recipe for Telegram/voice gateway
- `nginx.conf`: reverse proxy routes (including dashboard path)
- `deploy.sh`: server deployment helper for `/opt/pantheon`

## Current Compose Shape

The compose file currently enables the sandbox service by default and keeps additional services scaffolded/commented for staged rollout.

Active by default:

- `sandbox` on port `9000`

Prepared but currently commented:

- `agents`
- `gateway`
- `nginx`

## Persistent Data

- `samples` volume: sample files and analysis artifacts
- `db` volume: SQLite data (`pantheon.db`)

## Deployment Flow

`deploy.sh` expects:

- repository at `/opt/pantheon`
- valid `.env` in repo root
- Docker and Docker Compose installed on target host

Typical flow:

1. Pull latest `master`
2. Validate `.env`
3. Build containers
4. Start services
5. Wait for sandbox health check

## Operational Commands

From repo root:

```bash
docker compose -f infra/docker-compose.yml build
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps
docker compose -f infra/docker-compose.yml logs -f sandbox
```

## Security Notes

- Never embed secrets in compose or Dockerfiles; use `.env`.
- Follow malware-safety boundaries in `../CLAUDE.md`.
- Keep outbound restrictions and VPS isolation in place for live detonation workflows.
