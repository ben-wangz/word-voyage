#!/bin/sh
set -e

if [ "$1" != "backend" ] && [ "$1" != "frontend" ]; then
    echo "Usage: $0 <backend|frontend> [eslint-args...]"
    exit 1
fi

TARGET="$1"
shift

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/$TARGET"

podman run --rm -v .:/app:z -w /app m.daocloud.io/docker.io/oven/bun:1.1-alpine bun run lint "$@"
