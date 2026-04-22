#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker build \
  -f "$ROOT_DIR/npo-worker/Dockerfile" \
  -t npo-cli-worker:latest \
  "$ROOT_DIR"
