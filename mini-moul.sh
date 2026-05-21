#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return
  fi

  printf 'uv is required to bootstrap mini-moul.\n' >&2
  printf 'Install uv, then rerun this script.\n' >&2
  exit 1
}

bootstrap_tool() {
  uv tool install --editable --force "$REPO_ROOT" >/dev/null
}

main() {
  ensure_uv
  bootstrap_tool
  exec uv tool run --from "$REPO_ROOT" mini-moul "$@"
}

main "$@"
