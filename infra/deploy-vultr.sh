#!/usr/bin/env bash
# Local helper: deploy Pantheon backend to a Vultr VPS in one command.
#
# This script runs on your local machine and calls infra/deploy.sh on the remote host.
# It supports SSH key auth (recommended) or password auth via sshpass.
set -euo pipefail

REPO_DIR="/opt/pantheon"
BRANCH="master"
SET_WEBHOOK="false"
SKIP_PULL="false"
COPY_ENV="false"

HOST="${VULTR_SERVER_IP:-}"
USER_NAME="${VULTR_SERVER_USER:-root}"
PASSWORD="${VULTR_SERVER_PASS:-}"
SSH_KEY=""
REPO_URL=""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log() {
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  log "ERROR: $*"
  exit 1
}

usage() {
  cat <<'EOF'
Pantheon local -> Vultr deployment helper

Usage:
  ./infra/deploy-vultr.sh [options]

Options:
  --host <ip-or-hostname>   Vultr host (default: VULTR_SERVER_IP from .env)
  --user <username>         SSH user (default: VULTR_SERVER_USER or root)
  --password <password>     SSH password (default: VULTR_SERVER_PASS)
  --identity <key-path>     SSH private key path (recommended)
  --repo-url <git-url>      Repo URL to clone remotely if missing
  --repo-dir <path>         Remote repo path (default: /opt/pantheon)
  --branch <name>           Branch to deploy (default: master)
  --copy-env                Copy local .env to remote repo before deploy
  --set-webhook             Pass --set-webhook to remote deploy script
  --skip-pull               Pass --skip-pull to remote deploy script
  -h, --help                Show help

Examples:
  ./infra/deploy-vultr.sh --identity ~/.ssh/id_rsa --copy-env --set-webhook
  ./infra/deploy-vultr.sh --host 203.0.113.10 --password 'secret'
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="$2"
      shift 2
      ;;
    --user)
      USER_NAME="$2"
      shift 2
      ;;
    --password)
      PASSWORD="$2"
      shift 2
      ;;
    --identity)
      SSH_KEY="$2"
      shift 2
      ;;
    --repo-url)
      REPO_URL="$2"
      shift 2
      ;;
    --repo-dir)
      REPO_DIR="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --copy-env)
      COPY_ENV="true"
      shift
      ;;
    --set-webhook)
      SET_WEBHOOK="true"
      shift
      ;;
    --skip-pull)
      SKIP_PULL="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
done

# Load local .env defaults if present.
if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.env"
  set +a

  HOST="${HOST:-${VULTR_SERVER_IP:-}}"
  USER_NAME="${USER_NAME:-${VULTR_SERVER_USER:-root}}"
  PASSWORD="${PASSWORD:-${VULTR_SERVER_PASS:-}}"
fi

[[ -n "$HOST" ]] || die "Missing host. Set --host or VULTR_SERVER_IP in .env"

if [[ -z "$REPO_URL" ]]; then
  REPO_URL="$(git -C "$ROOT_DIR" config --get remote.origin.url || true)"
fi

if [[ -z "$SSH_KEY" && -z "$PASSWORD" ]]; then
  log "No --identity or --password provided. Falling back to default ssh agent/key behavior."
fi

if [[ -n "$SSH_KEY" ]]; then
  [[ -f "$SSH_KEY" ]] || die "SSH key file not found: $SSH_KEY"
fi

build_ssh_cmd() {
  if [[ -n "$SSH_KEY" ]]; then
    printf "ssh -i %q -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10" "$SSH_KEY"
  else
    printf "ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10"
  fi
}

build_scp_cmd() {
  if [[ -n "$SSH_KEY" ]]; then
    printf "scp -i %q -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10" "$SSH_KEY"
  else
    printf "scp -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10"
  fi
}

SSH_BASE="$(build_ssh_cmd)"
SCP_BASE="$(build_scp_cmd)"

if [[ -n "$PASSWORD" && -z "$SSH_KEY" ]]; then
  command -v sshpass >/dev/null 2>&1 || die "Password auth requires sshpass (brew install hudochenkov/sshpass/sshpass)"
  SSH_BASE="sshpass -p $(printf %q "$PASSWORD") $SSH_BASE"
  SCP_BASE="sshpass -p $(printf %q "$PASSWORD") $SCP_BASE"
fi

REMOTE="$USER_NAME@$HOST"

log "Checking SSH connectivity to $REMOTE..."
eval "$SSH_BASE" "$REMOTE" "echo connected" >/dev/null

log "Ensuring remote repo directory exists at $REPO_DIR..."
if [[ -n "$REPO_URL" ]]; then
  eval "$SSH_BASE" "$REMOTE" "mkdir -p $(printf %q "$REPO_DIR") && if [ ! -d $(printf %q "$REPO_DIR/.git") ]; then git clone $(printf %q "$REPO_URL") $(printf %q "$REPO_DIR"); fi"
else
  eval "$SSH_BASE" "$REMOTE" "mkdir -p $(printf %q "$REPO_DIR")"
fi

if [[ "$COPY_ENV" == "true" ]]; then
  [[ -f "$ROOT_DIR/.env" ]] || die "--copy-env requested but local .env not found"
  log "Copying local .env to remote host..."
  eval "$SCP_BASE" "$(printf %q "$ROOT_DIR/.env")" "$REMOTE:$(printf %q "$REPO_DIR/.env")"
fi

REMOTE_ARGS=("--repo-dir" "$REPO_DIR" "--branch" "$BRANCH")
if [[ "$SET_WEBHOOK" == "true" ]]; then
  REMOTE_ARGS+=("--set-webhook")
fi
if [[ "$SKIP_PULL" == "true" ]]; then
  REMOTE_ARGS+=("--skip-pull")
fi

remote_cmd="cd $(printf %q "$REPO_DIR") && chmod +x infra/deploy.sh && ./infra/deploy.sh"
for arg in "${REMOTE_ARGS[@]}"; do
  remote_cmd+=" $(printf %q "$arg")"
done

log "Running remote deployment script..."
eval "$SSH_BASE" "$REMOTE" "$remote_cmd"

log "Remote deployment finished successfully."