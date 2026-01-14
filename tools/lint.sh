#!/bin/bash

# ==========================================
# WordVoyage - Unified Lint Script
# ==========================================
#
# Usage:
#   tools/lint.sh <module> [lint-args...]
#
# Arguments:
#   module        Module to lint: llm, frontend, backend
#   lint-args     Additional arguments passed to linter
#
# Examples:
#   tools/lint.sh llm
#   tools/lint.sh frontend --fix
#   tools/lint.sh backend

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse arguments
MODULE=""
LINT_ARGS=()

for arg in "$@"; do
    if [ -z "$MODULE" ]; then
        MODULE="$arg"
    else
        LINT_ARGS+=("$arg")
    fi
done

# Validate module
if [ -z "$MODULE" ]; then
    echo -e "${RED}Error: Module is required${NC}"
    echo "Usage: $0 <module> [lint-args...]"
    echo "Modules: llm, frontend, backend"
    exit 1
fi

if [ "$MODULE" != "backend" ] && [ "$MODULE" != "frontend" ] && [ "$MODULE" != "llm" ]; then
    echo -e "${RED}Error: Invalid module: $MODULE${NC}"
    echo "Valid modules: llm, frontend, backend"
    exit 1
fi

MODULE_DIR="$PROJECT_ROOT/$MODULE"

if [ ! -d "$MODULE_DIR" ]; then
    echo -e "${RED}Error: Module directory not found: $MODULE_DIR${NC}"
    exit 1
fi

# Detect container runtime (prefer podman)
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
else
    echo -e "${RED}Error: Neither podman nor docker found${NC}"
    exit 1
fi

echo -e "${BLUE}=========================================="
echo "  Linting WordVoyage - $MODULE"
echo -e "==========================================${NC}"
echo ""
echo "Container runtime: $CONTAINER_RUNTIME"
echo "Module directory: $MODULE_DIR"
if [ ${#LINT_ARGS[@]} -gt 0 ]; then
    echo "Additional arguments: ${LINT_ARGS[*]}"
fi
echo ""

# Run linter
if [ "$MODULE" = "llm" ]; then
    echo -e "${BLUE}Running ruff check...${NC}"
    $CONTAINER_RUNTIME run --rm -v "$MODULE_DIR:/app:z" -w /app \
        m.daocloud.io/docker.io/python:3.11-slim \
        sh -c "pip install --no-cache-dir ruff >/dev/null 2>&1 && ruff check src ${LINT_ARGS[*]}"
else
    echo -e "${BLUE}Running bun lint...${NC}"
    $CONTAINER_RUNTIME run --rm -v "$MODULE_DIR:/app:z" -w /app \
        m.daocloud.io/docker.io/oven/bun:1.1-alpine \
        bun run lint "${LINT_ARGS[@]}"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  Lint completed successfully!"
    echo -e "==========================================${NC}"
else
    echo ""
    echo -e "${RED}=========================================="
    echo "  Lint failed!"
    echo -e "==========================================${NC}"
    exit 1
fi
