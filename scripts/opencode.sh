#!/usr/bin/env bash
# Wrapper that ensures DASHSCOPE_API_KEY is set before launching opencode.
# The Python fallback script auto-loads .env, but opencode itself doesn't.
# Use: ./scripts/opencode.sh [args...]  —  or alias it.

set -euo pipefail
HUB_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Load .env if it exists
if [ -f "$HUB_DIR/.env" ]; then
    set -a
    source "$HUB_DIR/.env"
    set +a
fi

exec opencode "$@"
