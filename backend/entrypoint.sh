#!/bin/sh

set -e

echo "Starting WordVoyage Backend Service..."
echo "Environment: ${NODE_ENV:-development}"
echo "Port: ${PORT:-8080}"
echo "Log Level: ${LOG_LEVEL:-info}"

exec bun run src/index.ts
