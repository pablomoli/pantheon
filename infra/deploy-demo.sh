#!/usr/bin/env bash
# One-command Pantheon demo deployment.
#
# Runs local -> remote deployment by invoking infra/deploy-vultr.sh,
# which then executes infra/deploy.sh on the VPS.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "$ROOT_DIR/infra/deploy-vultr.sh" ]]; then
  echo "ERROR: infra/deploy-vultr.sh is missing or not executable."
  exit 1
fi

echo "Starting one-command demo deployment..."
echo "This will run local wrapper + remote server deploy in sequence."

"$ROOT_DIR/infra/deploy-vultr.sh" "$@"

echo "Pantheon demo deploy finished."