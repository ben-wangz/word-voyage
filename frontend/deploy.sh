#!/bin/bash
# Deployment script for WordVoyage Frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
CONTAINER_PREFIX="${CONTAINER_PREFIX:-wordvoyage-frontend}"
IMAGE_NAME="wordvoyage-frontend:latest"

# Default values
ACTION=""
BUILD_IMAGE=0
PORT=3000

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment from .env file
load_env_file() {
    local env_file="$SCRIPT_DIR/.env"
    if [ -f "$env_file" ]; then
        log_info "Loading configuration from .env file"
        set -a
        source "$env_file"
        set +a
    else
        log_warn ".env file not found at $env_file"
    fi
}

# Collect environment variables with SERVICE_ prefix
collect_env_vars() {
    local env_args=""
    while IFS='=' read -r name value; do
        if [[ $name == SERVICE_* ]]; then
            local clean_name="${name#SERVICE_}"
            env_args="$env_args -e ${clean_name}=${value}"
        fi
    done < <(env)
    echo "$env_args"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --action)
            ACTION="$2"
            shift 2
            ;;
        --build)
            BUILD_IMAGE=1
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 --action <action> [OPTIONS]"
            echo ""
            echo "Actions:"
            echo "  start      Start the WordVoyage frontend"
            echo "  stop       Stop the WordVoyage frontend"
            echo ""
            echo "Options:"
            echo "  --build         Build the Docker image before starting"
            echo "  --port PORT     Port to expose the service (default: 3000)"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --action start              # Start the service"
            echo "  $0 --action start --build      # Build and start the service"
            echo "  $0 --action stop               # Stop the service"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate arguments
if [ -z "$ACTION" ]; then
    log_error "Missing required argument: --action"
    exit 1
fi

ACTION=$(echo "$ACTION" | tr '[:upper:]' '[:lower:]')

if [ "$ACTION" != "start" ] && [ "$ACTION" != "stop" ]; then
    log_error "Invalid action: $ACTION (must be 'start' or 'stop')"
    exit 1
fi

# Stop service
stop_app() {
    if podman ps -a --filter "name=${CONTAINER_PREFIX}" --format "{{.Names}}" | grep -q "^${CONTAINER_PREFIX}$"; then
        log_info "Stopping WordVoyage frontend container: ${CONTAINER_PREFIX}"
        podman stop "${CONTAINER_PREFIX}" >/dev/null 2>&1 || true
        podman rm "${CONTAINER_PREFIX}" >/dev/null 2>&1 || true
    else
        log_info "WordVoyage frontend container not found, skipping"
    fi
}

# Start service
start_app() {
    if [ $BUILD_IMAGE -eq 1 ]; then
        log_info "Building WordVoyage frontend image..."
        bash "$SCRIPT_DIR/build.sh"
    fi

    log_info "Starting WordVoyage Frontend Service..."

    stop_app

    load_env_file

    local env_vars=$(collect_env_vars)

    podman run -d \
        --name "${CONTAINER_PREFIX}" \
        -p "${PORT}:3000" \
        $env_vars \
        "$IMAGE_NAME"

    log_info "WordVoyage Frontend Service started"
    log_info "Service URL: http://localhost:${PORT}"
}

# Main execution
log_info "========================================="
log_info "WordVoyage Frontend Deployment"
log_info "========================================="
log_info "Action: $ACTION"
log_info "Container name: $CONTAINER_PREFIX"
log_info "========================================="

if [ "$ACTION" = "start" ]; then
    start_app
elif [ "$ACTION" = "stop" ]; then
    stop_app
fi

log_info "========================================="
log_info "Completed: $ACTION"
log_info "========================================="
