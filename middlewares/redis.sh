#!/bin/bash

# Redis middleware script for word-voyage

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CONTAINER_NAME="word-voyage-redis"
REDIS_IMAGE="m.daocloud.io/docker.io/redis:latest"
REDIS_PORT="6379"
REDIS_DATA_DIR="${SCRIPT_DIR}/data/redis"

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

stop_redis() {
    if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_info "Stopping ${CONTAINER_NAME}..."
        podman stop "${CONTAINER_NAME}" 2>/dev/null || true
        podman rm "${CONTAINER_NAME}" 2>/dev/null || true
    fi
}

start_redis() {
    stop_redis

    mkdir -p "${REDIS_DATA_DIR}"

    log_info "Starting Redis container..."
    podman run -d \
        --name "${CONTAINER_NAME}" \
        -p "${REDIS_PORT}:6379" \
        -v "${REDIS_DATA_DIR}:/data:rw" \
        "${REDIS_IMAGE}" \
        redis-server --appendonly yes

    log_info "Waiting for Redis to be ready..."
    sleep 2

    log_info "Redis started successfully"
    log_info "  Server: localhost:${REDIS_PORT}"
}

status_redis() {
    if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_info "Redis is running"
        podman ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        log_info "Redis is not running"
    fi
}

case "${1:-}" in
    start)
        start_redis
        ;;
    stop)
        stop_redis
        log_info "Redis stopped"
        ;;
    restart)
        start_redis
        ;;
    status)
        status_redis
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
