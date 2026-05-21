#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
BIN_DIR="${XDG_BIN_HOME:-${HOME}/.local/bin}"
TOOL_BIN="$BIN_DIR/mini-moul"

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

  if [[ ! -x "$TOOL_BIN" ]]; then
    printf 'mini-moul was installed, but the binary was not found at %s.\n' "$TOOL_BIN" >&2
    printf 'Ensure %s exists and is on PATH.\n' "$BIN_DIR" >&2
    exit 1
  fi

  exec "$TOOL_BIN" "$@"
}

main "$@"
