#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker compose \
  -f "$ROOT_DIR/npo-submit/docker-compose.yml" \
  run --rm npo-cli-submit "$@"
