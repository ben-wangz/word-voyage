#!/bin/sh

set -e

echo "Starting WordVoyage Backend Service..."
echo "Environment: ${NODE_ENV:-development}"
echo "Port: ${PORT:-8080}"

exec bun run src/index.ts
