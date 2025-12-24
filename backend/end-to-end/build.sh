#!/bin/bash

# ==========================================
# Backend E2E Test - Build Script
# ==========================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME=${IMAGE_NAME:-"backend-e2e"}
VERSION=${VERSION:-"1.0.0"}
TAG="${IMAGE_NAME}:${VERSION}"
TAG_LATEST="${IMAGE_NAME}:latest"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# PyPI repository URL (optional)
PIP_INDEX_URL=${PIP_INDEX_URL:-""}
PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST:-""}

echo -e "${BLUE}=========================================="
echo "  Building Backend E2E Test Image"
echo -e "==========================================${NC}"
echo ""
echo "Image tags:"
echo "  - $TAG"
echo "  - $TAG_LATEST"
echo ""
echo "Containerfile: $SCRIPT_DIR/Containerfile"
echo "Build context: $SCRIPT_DIR"
echo ""

# Display PyPI configuration if provided
if [ -n "$PIP_INDEX_URL" ]; then
    echo -e "${YELLOW}Custom PyPI Repository:${NC}"
    echo "  URL: $PIP_INDEX_URL"
    if [ -n "$PIP_TRUSTED_HOST" ]; then
        echo "  Trusted Host: $PIP_TRUSTED_HOST"
    fi
    echo ""
fi

# Build command with optional build arguments
BUILD_CMD="podman build -f $SCRIPT_DIR/Containerfile"

# Add PyPI configuration as build arguments if provided
if [ -n "$PIP_INDEX_URL" ]; then
    BUILD_CMD="$BUILD_CMD --build-arg PIP_INDEX_URL=\"$PIP_INDEX_URL\""
    if [ -n "$PIP_TRUSTED_HOST" ]; then
        BUILD_CMD="$BUILD_CMD --build-arg PIP_TRUSTED_HOST=\"$PIP_TRUSTED_HOST\""
    fi
fi

# Add tags
BUILD_CMD="$BUILD_CMD -t \"$TAG\" -t \"$TAG_LATEST\" $SCRIPT_DIR"

# Build the image
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
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
