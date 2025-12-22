#!/bin/sh

# Frontend service entrypoint
set -e

# Set default configuration
export FRONTEND_PORT=${FRONTEND_PORT:-3000}
export BACKEND_HOST=${BACKEND_HOST:-host.containers.internal}
export BACKEND_PORT=${BACKEND_PORT:-8080}

echo "[INFO] Starting WordVoyage Frontend Service..."
echo "[INFO] Environment: $NODE_ENV"
echo "[INFO] Frontend Port: $FRONTEND_PORT"
echo "[INFO] Backend URL: http://${BACKEND_HOST}:${BACKEND_PORT}"

# Replace environment variables in nginx config
envsubst '$FRONTEND_PORT $BACKEND_HOST $BACKEND_PORT' < /etc/nginx/conf.d/default.conf > /tmp/nginx.conf.tmp
mv /tmp/nginx.conf.tmp /etc/nginx/conf.d/default.conf

# Start nginx in foreground
exec nginx -g "daemon off;"
