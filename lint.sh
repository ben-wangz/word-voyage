#!/bin/sh
set -e

if [ "$1" != "backend" ] && [ "$1" != "frontend" ] && [ "$1" != "llm" ]; then
    echo "Usage: $0 <backend|frontend|llm> [lint-args...]"
    exit 1
fi

TARGET="$1"
shift

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/$TARGET"

if [ "$TARGET" = "llm" ]; then
    podman run --rm -v .:/app:z -w /app m.daocloud.io/docker.io/python:3.11-slim sh -c "pip install --no-cache-dir ruff >/dev/null 2>&1 && ruff check src $*"
else
    podman run --rm -v .:/app:z -w /app m.daocloud.io/docker.io/oven/bun:1.1-alpine bun run lint "$@"
fi
