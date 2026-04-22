#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker build \
  -f "$ROOT_DIR/npo-submit/Dockerfile" \
  -t npo-cli-submit:latest \
  "$ROOT_DIR"
