#!/bin/bash
# End-to-end test orchestration script for Frontend Service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_SCRIPT="$PROJECT_ROOT/../tools/deploy.sh"
MODULE="frontend"

# Configuration
BROWSERLESS_IMAGE="ghcr.io/browserless/chromium:latest"
BROWSERLESS_PORT=3003
BROWSERLESS_CONTAINER="word-voyage-browserless-e2e"
SCREENSHOTS_DIR="$SCRIPT_DIR/build/screenshots"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Collect environment variables with TEST_ prefix
collect_test_env_vars() {
    local env_args=""
    while IFS='=' read -r name value; do
        if [[ $name == TEST_* ]]; then
            local clean_name="${name#TEST_}"
            env_args="$env_args -e ${clean_name}=${value}"
        fi
    done < <(env)
    echo "$env_args"
}

# Parse command line arguments
CLEANUP_ONLY=0
SKIP_BUILD=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --cleanup-only)
            CLEANUP_ONLY=1
            shift
            ;;
        --skip-build)
            SKIP_BUILD=1
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --cleanup-only      Only cleanup test containers"
            echo "  --skip-build        Skip building the Frontend image"
            echo "  --help, -h          Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to project root
cd "$PROJECT_ROOT"

# Cleanup function
cleanup() {
    log_info "Cleaning up after 15 seconds..."
    sleep 15

    # Stop and remove browserless container
    if [ ! -z "$BROWSERLESS_CONTAINER_ID" ]; then
        podman rm -f "$BROWSERLESS_CONTAINER_ID" 2>/dev/null || true
    fi

    # Stop frontend service
    bash "$DEPLOY_SCRIPT" "$MODULE" --action stop
}

# Set trap for cleanup on exit
trap cleanup EXIT

# If only cleanup requested
if [ $CLEANUP_ONLY -eq 1 ]; then
    cleanup
    exit 0
fi

# Main test flow
log_info "=========================================="
log_info "Frontend E2E Test Suite"
log_info "=========================================="
log_warn "This test assumes Backend service is already running."
log_warn "Please start it first if not running."
log_info ""

log_info "Step 1: Starting Frontend Service..."
if [ $SKIP_BUILD -eq 0 ]; then
    log_info "Building Frontend image..."
    bash "$DEPLOY_SCRIPT" "$MODULE" --action start --build
else
    log_info "Skipping build (--skip-build flag set)"
    bash "$DEPLOY_SCRIPT" "$MODULE" --action start
fi

sleep 3

log_info ""
log_info "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        log_info "Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Frontend failed to start within 30 seconds"
        bash "$DEPLOY_SCRIPT" "$MODULE" --action stop
        exit 1
    fi
    echo -n "."
    sleep 1
done

# Create screenshots directory
mkdir -p "$SCREENSHOTS_DIR"
log_info "Screenshots will be saved to: $SCREENSHOTS_DIR"

log_info ""
log_info "Step 2: Starting Browserless Chromium container..."
BROWSERLESS_CONTAINER_ID=$(podman run -d \
    --name "$BROWSERLESS_CONTAINER" \
    -p "$BROWSERLESS_PORT:3003" \
    -e "PORT=3003" \
    -e "TIMEOUT=300000" \
    -e "CONNECTION_TIMEOUT=300000" \
    "$BROWSERLESS_IMAGE")

log_info "Browserless container started: $BROWSERLESS_CONTAINER_ID"

# Wait for Browserless to be ready
log_info "Waiting for Browserless to be ready..."
for i in {1..30}; do
    if curl -s "http://localhost:$BROWSERLESS_PORT/health" > /dev/null 2>&1; then
        log_info "Browserless is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Browserless failed to start"
        exit 1
    fi
    echo -n "."
    sleep 1
done

log_info ""
log_info "Building test image..."
bash "$SCRIPT_DIR/../tools/build.sh" frontend

log_info ""
log_info "Step 3: Running tests in container..."
log_info "Executing tests..."

# Collect TEST_ environment variables
TEST_ENV_VARS=$(collect_test_env_vars)

podman run --rm \
    -v "$SCREENSHOTS_DIR:/app/screenshots" \
    $TEST_ENV_VARS \
    frontend-e2e:latest
