#!/bin/bash

# ==========================================
# WordVoyage - Unified Deployment Script
# ==========================================
#
# Usage:
#   tools/deploy.sh <module> --action <start|stop> [OPTIONS]
#
# Arguments:
#   module              Module to deploy: llm, frontend, backend
#   --action ACTION     Action to perform: start, stop
#
# Options:
#   --build             Build image before starting
#   --port PORT         Override default port
#   --help, -h          Show help message
#
# Configuration:
#   Each module requires a deploy.yaml file in its directory
#
# Examples:
#   tools/deploy.sh llm --action start
#   tools/deploy.sh frontend --action start --build --port 3001
#   tools/deploy.sh backend --action stop

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

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if yq is available and can parse YAML
check_yq() {
    if ! command -v yq &> /dev/null; then
        log_error "yq is not installed"
        log_error "Please install yq: https://github.com/mikefarah/yq"
        log_error "  - Ubuntu/Debian: wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq && chmod +x /usr/local/bin/yq"
        log_error "  - macOS: brew install yq"
        exit 1
    fi

    # Test if yq can parse YAML (distinguish from other tools with same name)
    if ! echo "test: value" | yq eval '.test' - &> /dev/null; then
        log_error "yq found but cannot parse YAML"
        log_error "Please ensure you have the correct yq installed: https://github.com/mikefarah/yq"
        exit 1
    fi
}

# Parse arguments
MODULE=""
ACTION=""
BUILD_IMAGE=0
PORT_OVERRIDE=""

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
            PORT_OVERRIDE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 <module> --action <action> [OPTIONS]"
            echo ""
            echo "Arguments:"
            echo "  module              Module to deploy: llm, frontend, backend"
            echo ""
            echo "Actions:"
            echo "  start               Start the service"
            echo "  stop                Stop the service"
            echo ""
            echo "Options:"
            echo "  --build             Build the image before starting"
            echo "  --port PORT         Override default port"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  CONTAINER_PREFIX    Override container name"
            echo "  SERVICE_*           Pass environment variables to container (prefix removed)"
            echo ""
            echo "Examples:"
            echo "  $0 llm --action start"
            echo "  $0 frontend --action start --build --port 3001"
            echo "  $0 backend --action stop"
            exit 0
            ;;
        -*)
            log_error "Unknown option: $1"
            exit 1
            ;;
        *)
            if [ -z "$MODULE" ]; then
                MODULE="$1"
            else
                log_error "Unexpected argument: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate module
if [ -z "$MODULE" ]; then
    log_error "Module is required"
    echo "Usage: $0 <module> --action <action> [OPTIONS]"
    echo "Modules: llm, frontend, backend"
    exit 1
fi

MODULE_DIR="$PROJECT_ROOT/$MODULE"

if [ ! -d "$MODULE_DIR" ]; then
    log_error "Module directory not found: $MODULE_DIR"
    exit 1
fi

# Validate action
if [ -z "$ACTION" ]; then
    log_error "Missing required argument: --action"
    exit 1
fi

ACTION=$(echo "$ACTION" | tr '[:upper:]' '[:lower:]')

if [ "$ACTION" != "start" ] && [ "$ACTION" != "stop" ]; then
    log_error "Invalid action: $ACTION (must be 'start' or 'stop')"
    exit 1
fi

# Check yq before loading config
check_yq

# Load configuration from deploy.yaml
CONFIG_FILE="$MODULE_DIR/deploy.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    log_error "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Read configuration
SERVICE_NAME=$(yq eval '.name' "$CONFIG_FILE")
CONTAINER_PREFIX_DEFAULT=$(yq eval '.container_name' "$CONFIG_FILE")
IMAGE_NAME_DEFAULT=$(yq eval '.image_name' "$CONFIG_FILE")
DEFAULT_PORT=$(yq eval '.default_port' "$CONFIG_FILE")
INTERNAL_PORT=$(yq eval '.internal_port' "$CONFIG_FILE")
HEALTH_CHECK=$(yq eval '.health_check' "$CONFIG_FILE")

# Allow environment variable override
CONTAINER_PREFIX="${CONTAINER_PREFIX:-$CONTAINER_PREFIX_DEFAULT}"
IMAGE_NAME="${IMAGE_NAME:-$IMAGE_NAME_DEFAULT}:latest"
PORT="${PORT_OVERRIDE:-$DEFAULT_PORT}"

# Detect container runtime (prefer podman)
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
else
    log_error "Neither podman nor docker found"
    exit 1
fi

# Load environment from .env file
load_env_file() {
    local env_file="$MODULE_DIR/.env"
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

# Stop service
stop_app() {
    if $CONTAINER_RUNTIME ps -a --filter "name=${CONTAINER_PREFIX}" --format "{{.Names}}" | grep -q "^${CONTAINER_PREFIX}$"; then
        log_info "Stopping $SERVICE_NAME container: ${CONTAINER_PREFIX}"
        $CONTAINER_RUNTIME stop "${CONTAINER_PREFIX}" >/dev/null 2>&1 || true
        $CONTAINER_RUNTIME rm "${CONTAINER_PREFIX}" >/dev/null 2>&1 || true
    else
        log_info "$SERVICE_NAME container not found, skipping"
    fi
}

# Start service
start_app() {
    if [ $BUILD_IMAGE -eq 1 ]; then
        log_info "Building $SERVICE_NAME image..."
        bash "$SCRIPT_DIR/build.sh" "$MODULE"
    fi

    log_info "Starting $SERVICE_NAME..."

    stop_app

    load_env_file

    local env_vars=$(collect_env_vars)

    $CONTAINER_RUNTIME run -d \
        --name "${CONTAINER_PREFIX}" \
        -p "${PORT}:${INTERNAL_PORT}" \
        $env_vars \
        "$IMAGE_NAME"

    log_info "$SERVICE_NAME started"
    log_info "Service URL: http://localhost:${PORT}"
    if [ "$HEALTH_CHECK" != "null" ] && [ -n "$HEALTH_CHECK" ]; then
        log_info "Health check: http://localhost:${PORT}${HEALTH_CHECK}"
    fi
}

# Main execution
log_info "========================================="
log_info "$SERVICE_NAME Deployment"
log_info "========================================="
log_info "Module: $MODULE"
log_info "Action: $ACTION"
log_info "Container runtime: $CONTAINER_RUNTIME"
log_info "Container name: $CONTAINER_PREFIX"
log_info "Port: $PORT"
log_info "========================================="

if [ "$ACTION" = "start" ]; then
    start_app
elif [ "$ACTION" = "stop" ]; then
    stop_app
fi

log_info "========================================="
log_info "Completed: $ACTION"
log_info "========================================="
