#!/bin/bash

# ==========================================
# WordVoyage - Unified Build Script
# ==========================================
#
# Usage:
#   tools/build.sh <module> [--push]
#
# Arguments:
#   module    Module to build: llm, frontend, backend
#   --push    Push image after build (default: no push)
#
# Environment Variables:
#   IMAGE_NAME    Override image name (default: wordvoyage-<module>)
#   VERSION       Override version (default: read from <module>/VERSION)
#   BUILD_ARG_*   Pass build arguments to container build
#
# Examples:
#   tools/build.sh llm
#   tools/build.sh frontend --push
#   IMAGE_NAME=ghcr.io/user/my-image VERSION=2.0.0 tools/build.sh backend --push

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
PUSH=false

for arg in "$@"; do
    case $arg in
        --push)
            PUSH=true
            ;;
        -*)
            echo -e "${RED}Unknown option: $arg${NC}"
            exit 1
            ;;
        *)
            if [ -z "$MODULE" ]; then
                MODULE="$arg"
            else
                echo -e "${RED}Unexpected argument: $arg${NC}"
                exit 1
            fi
            ;;
    esac
done

# Validate module
if [ -z "$MODULE" ]; then
    echo -e "${RED}Error: Module is required${NC}"
    echo "Usage: $0 <module> [--push]"
    echo "Modules: llm, frontend, backend"
    exit 1
fi

MODULE_DIR="$PROJECT_ROOT/$MODULE"

if [ ! -d "$MODULE_DIR" ]; then
    echo -e "${RED}Error: Module directory not found: $MODULE_DIR${NC}"
    exit 1
fi

if [ ! -f "$MODULE_DIR/Containerfile" ]; then
    echo -e "${RED}Error: Containerfile not found: $MODULE_DIR/Containerfile${NC}"
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

# Read version from VERSION file if not set
if [ -z "$VERSION" ]; then
    VERSION_FILE="$MODULE_DIR/VERSION"
    if [ -f "$VERSION_FILE" ]; then
        VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')
    else
        VERSION="1.0.0"
        echo -e "${YELLOW}Warning: VERSION file not found, using default: $VERSION${NC}"
    fi
fi

# Set default image name if not provided
if [ -z "$IMAGE_NAME" ]; then
    IMAGE_NAME="wordvoyage-$MODULE"
fi

TAG="${IMAGE_NAME}:${VERSION}"
TAG_LATEST="${IMAGE_NAME}:latest"

# Collect build arguments with BUILD_ARG_ prefix
collect_build_args() {
    local build_args=""
    while IFS='=' read -r name value; do
        if [[ $name == BUILD_ARG_* ]]; then
            local clean_name="${name#BUILD_ARG_}"
            build_args="$build_args --build-arg ${clean_name}=${value}"
        fi
    done < <(env)
    echo "$build_args"
}

echo -e "${BLUE}=========================================="
echo "  Building WordVoyage - $MODULE"
echo -e "==========================================${NC}"
echo ""
echo "Container runtime: $CONTAINER_RUNTIME"
echo "Image tags:"
echo "  - $TAG"
echo "  - $TAG_LATEST"
echo ""
echo "Containerfile: $MODULE_DIR/Containerfile"
echo "Build context: $MODULE_DIR"
if [ "$PUSH" = true ]; then
    echo -e "Push: ${GREEN}enabled${NC}"
else
    echo "Push: disabled"
fi
echo ""

BUILD_ARGS=$(collect_build_args)

if [ -n "$BUILD_ARGS" ]; then
    echo -e "${YELLOW}Build Arguments:${NC}"
    env | grep "^BUILD_ARG_" | while IFS='=' read -r name value; do
        clean_name="${name#BUILD_ARG_}"
        echo "  ${clean_name}: ${value}"
    done
    echo ""
fi

# Build command
BUILD_CMD="$CONTAINER_RUNTIME build -f $MODULE_DIR/Containerfile"

if [ -n "$BUILD_ARGS" ]; then
    BUILD_CMD="$BUILD_CMD $BUILD_ARGS"
fi

BUILD_CMD="$BUILD_CMD -t $TAG -t $TAG_LATEST $MODULE_DIR"

echo -e "${BLUE}Building image...${NC}"
echo "Command: $BUILD_CMD"
echo ""
eval $BUILD_CMD

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo "  Build completed successfully!"
echo -e "==========================================${NC}"
echo ""

# Push if requested
if [ "$PUSH" = true ]; then
    echo -e "${BLUE}Pushing images...${NC}"
    echo ""

    echo "Pushing $TAG..."
    $CONTAINER_RUNTIME push "$TAG"

    echo "Pushing $TAG_LATEST..."
    $CONTAINER_RUNTIME push "$TAG_LATEST"

    echo ""
    echo -e "${GREEN}=========================================="
    echo "  Push completed successfully!"
    echo -e "==========================================${NC}"
fi

echo ""
echo "Image tags:"
echo "  - $TAG"
echo "  - $TAG_LATEST"
echo ""
