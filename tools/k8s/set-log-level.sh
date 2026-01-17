#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELEASE_NAME="${RELEASE_NAME:-word-voyage}"
NAMESPACE="${NAMESPACE:-default}"
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"

usage() {
    echo "Usage: $0 <module> <log-level>"
    echo ""
    echo "Arguments:"
    echo "  module      Module to update: frontend, backend, llm"
    echo "  log-level   Log level: DEBUG, INFO, WARN, ERROR"
    echo ""
    echo "Environment Variables:"
    echo "  RELEASE_NAME    Helm release name (default: word-voyage)"
    echo "  NAMESPACE       Kubernetes namespace (default: default)"
    echo "  KUBECONFIG      Kubeconfig path (default: /etc/rancher/k3s/k3s.yaml)"
    echo ""
    echo "Examples:"
    echo "  $0 backend DEBUG"
    echo "  $0 llm INFO"
    echo "  $0 frontend WARN"
    exit 1
}

check_requirements() {
    local missing=0

    for cmd in kubectl; do
        if ! command -v $cmd &>/dev/null; then
            echo -e "${RED}Error: $cmd not found${NC}"
            missing=1
        fi
    done

    if [ $missing -eq 1 ]; then
        exit 1
    fi

    if [ ! -f "$KUBECONFIG" ]; then
        echo -e "${RED}Error: KUBECONFIG not found: $KUBECONFIG${NC}"
        exit 1
    fi
}

MODULE="${1:-}"
LOG_LEVEL="${2:-}"

if [ -z "$MODULE" ] || [ -z "$LOG_LEVEL" ]; then
    usage
fi

case "$MODULE" in
    frontend|backend|llm)
        ;;
    *)
        echo -e "${RED}Error: Invalid module: $MODULE${NC}"
        usage
        ;;
esac

case "$LOG_LEVEL" in
    DEBUG|INFO|WARN|ERROR|debug|info|warn|error)
        LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')
        ;;
    *)
        echo -e "${RED}Error: Invalid log level: $LOG_LEVEL${NC}"
        echo "Valid levels: DEBUG, INFO, WARN, ERROR"
        exit 1
        ;;
esac

check_requirements

DEPLOYMENT_NAME="$RELEASE_NAME-$MODULE"

echo -e "${BLUE}=========================================="
echo "  Update Log Level - $MODULE"
echo -e "==========================================${NC}"
echo ""
echo "Release: $RELEASE_NAME"
echo "Namespace: $NAMESPACE"
echo "Deployment: $DEPLOYMENT_NAME"
echo "New log level: $LOG_LEVEL"
echo ""

# Check if deployment exists
if ! kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo -e "${RED}Error: Deployment not found: $DEPLOYMENT_NAME${NC}"
    exit 1
fi

# Get current env vars
echo -e "${BLUE}[1/3] Checking current environment variables...${NC}"
CURRENT_ENV=$(kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].env}')

if [ -z "$CURRENT_ENV" ] || [ "$CURRENT_ENV" = "null" ]; then
    echo "No environment variables found, will create new list"
    HAS_LOG_LEVEL=false
else
    # Check if LOG_LEVEL already exists
    if echo "$CURRENT_ENV" | grep -q '"name":"LOG_LEVEL"'; then
        echo "LOG_LEVEL environment variable exists, will update"
        HAS_LOG_LEVEL=true
    else
        echo "LOG_LEVEL environment variable not found, will add"
        HAS_LOG_LEVEL=false
    fi
fi

# Prepare patch operation
echo ""
echo -e "${BLUE}[2/3] Preparing patch operation...${NC}"

if [ "$HAS_LOG_LEVEL" = true ]; then
    # Update existing LOG_LEVEL
    # Find the index of LOG_LEVEL in env array
    ENV_INDEX=$(kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o json | \
        jq '.spec.template.spec.containers[0].env | to_entries | .[] | select(.value.name=="LOG_LEVEL") | .key')

    if [ -z "$ENV_INDEX" ]; then
        echo -e "${RED}Error: Failed to find LOG_LEVEL index${NC}"
        exit 1
    fi

    PATCH_JSON="[{\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/env/${ENV_INDEX}/value\", \"value\": \"$LOG_LEVEL\"}]"
else
    # Add new LOG_LEVEL to env array
    # Get current env array or create empty array
    CURRENT_ENV_JSON=$(kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o json | \
        jq '.spec.template.spec.containers[0].env // []')

    # Add new LOG_LEVEL entry
    NEW_ENV_JSON=$(echo "$CURRENT_ENV_JSON" | jq ". + [{\"name\": \"LOG_LEVEL\", \"value\": \"$LOG_LEVEL\"}]")

    PATCH_JSON="[{\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/env\", \"value\": $NEW_ENV_JSON}]"
fi

echo "Patch operation prepared"

# Apply patch
echo ""
echo -e "${BLUE}[3/3] Applying patch...${NC}"

kubectl patch deployment "$DEPLOYMENT_NAME" \
    -n "$NAMESPACE" \
    --type='json' \
    -p="$PATCH_JSON"

echo ""
echo "Waiting for rollout to complete..."
kubectl rollout status deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" --timeout=300s

echo ""
echo -e "${GREEN}=========================================="
echo "  Log level updated successfully!"
echo -e "==========================================${NC}"
echo ""
echo "Deployment: $DEPLOYMENT_NAME"
echo "Log level: $LOG_LEVEL"
echo ""
echo "Check logs:"
echo "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=$MODULE --tail=50 -f"
echo ""
