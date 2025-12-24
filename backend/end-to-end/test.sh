#!/bin/bash
# End-to-end test orchestration script for Backend Service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_SCRIPT="$PROJECT_ROOT/deploy.sh"

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
            echo "  --skip-build        Skip building the Backend image"
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
    bash "$DEPLOY_SCRIPT" --action stop
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
log_info "Backend E2E Test Suite"
log_info "=========================================="
log_warn "This test assumes LLM service is already running."
log_warn "Please start it first if not running."
log_info ""

log_info "Step 1: Starting Backend Service..."
log_info "Enabling DEBUG logging for backend service..."
export SERVICE_LOG_LEVEL=debug
if [ $SKIP_BUILD -eq 0 ]; then
    log_info "Building Backend image..."
    bash "$DEPLOY_SCRIPT" --action start --build
else
    log_info "Skipping build (--skip-build flag set)"
    bash "$DEPLOY_SCRIPT" --action start
fi

sleep 3

log_info ""
log_info "Waiting for service to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
        log_info "Service is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Service failed to start within 30 seconds"
        bash "$DEPLOY_SCRIPT" --action stop
        exit 1
    fi
    echo -n "."
    sleep 1
done

log_info ""
log_info "Building test image..."
bash "$SCRIPT_DIR/build.sh"

log_info ""
log_info "Step 2: Running tests in container..."
log_info "Executing tests..."
podman run --rm \
    backend-e2e:latest \
    python -m src.run_tests
