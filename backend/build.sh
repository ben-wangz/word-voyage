#!/bin/bash

# ==========================================
# WordVoyage Backend - Build Script
# ==========================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
IMAGE_NAME=${IMAGE_NAME:-"wordvoyage-backend"}
VERSION=${VERSION:-"1.0.0"}
TAG="${IMAGE_NAME}:${VERSION}"
TAG_LATEST="${IMAGE_NAME}:latest"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Collect build arguments with BUILD_ARG_ prefix
collect_build_args() {
    local build_args=""
    while IFS='=' read -r name value; do
        if [[ $name == BUILD_ARG_* ]]; then
            local clean_name="${name#BUILD_ARG_}"
            build_args="$build_args --build-arg ${clean_name}=\"${value}\""
        fi
    done < <(env)
    echo "$build_args"
}

echo -e "${BLUE}=========================================="
echo "  Building WordVoyage Backend"
echo -e "==========================================${NC}"
echo ""
echo "Image tags:"
echo "  - $TAG"
echo "  - $TAG_LATEST"
echo ""
echo "Containerfile: $SCRIPT_DIR/Containerfile"
echo "Build context: $SCRIPT_DIR"
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

BUILD_CMD="podman build -f $SCRIPT_DIR/Containerfile"

if [ -n "$BUILD_ARGS" ]; then
    BUILD_CMD="$BUILD_CMD $BUILD_ARGS"
fi

BUILD_CMD="$BUILD_CMD -t \"$TAG\" -t \"$TAG_LATEST\" $SCRIPT_DIR"

echo -e "${BLUE}Building image...${NC}"
echo "Command: $BUILD_CMD"
echo ""
eval $BUILD_CMD

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  Build completed successfully!"
    echo -e "==========================================${NC}"
    echo ""
    echo "Image tags:"
    echo "  - $TAG"
    echo "  - $TAG_LATEST"
    echo ""
    echo "Run the container:"
    echo ""
    echo "  podman run -d --name wordvoyage-backend \\"
    echo "    -p 8080:8080 \\"
    echo "    $TAG_LATEST"
    echo ""
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
