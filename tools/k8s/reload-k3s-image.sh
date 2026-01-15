#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RELEASE_NAME="${RELEASE_NAME:-word-voyage}"
NAMESPACE="${NAMESPACE:-default}"
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"

usage() {
    echo "Usage: $0 <module>"
    echo ""
    echo "Arguments:"
    echo "  module    Module to reload: frontend, backend, llm"
    echo ""
    echo "Environment Variables:"
    echo "  RELEASE_NAME    Helm release name (default: word-voyage)"
    echo "  NAMESPACE       Kubernetes namespace (default: default)"
    echo "  KUBECONFIG      Kubeconfig path (default: /etc/rancher/k3s/k3s.yaml)"
    echo ""
    echo "Examples:"
    echo "  $0 frontend"
    echo "  $0 backend"
    echo "  $0 llm"
    exit 1
}

check_requirements() {
    local missing=0

    for cmd in kubectl k3s; do
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

detect_container_runtime() {
    if command -v podman &>/dev/null; then
        echo "podman"
    elif command -v docker &>/dev/null; then
        echo "docker"
    else
        echo -e "${RED}Error: Neither podman nor docker found${NC}"
        exit 1
    fi
}

MODULE="${1:-}"
if [ -z "$MODULE" ]; then
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

check_requirements
CONTAINER_RUNTIME=$(detect_container_runtime)

echo -e "${BLUE}=========================================="
echo "  Quick Reload - $MODULE"
echo -e "==========================================${NC}"
echo ""
echo "Release: $RELEASE_NAME"
echo "Namespace: $NAMESPACE"
echo "Container runtime: $CONTAINER_RUNTIME"
echo ""

# Step 1: Build image
echo -e "${BLUE}[1/4] Building image...${NC}"
"$PROJECT_ROOT/tools/build.sh" "$MODULE"

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

# Read version
VERSION_FILE="$PROJECT_ROOT/$MODULE/VERSION"
if [ -f "$VERSION_FILE" ]; then
    VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')
else
    VERSION="1.0.0"
fi

IMAGE_NAME="wordvoyage-$MODULE"
DEV_TAG="${VERSION}-dev-$(date +%s)"
SOURCE_TAG="${IMAGE_NAME}:${VERSION}"
TARGET_TAG="${IMAGE_NAME}:${DEV_TAG}"

echo ""
echo -e "${BLUE}[2/4] Tagging image for dev deployment...${NC}"
echo "Source: $SOURCE_TAG"
echo "Target: $TARGET_TAG"
$CONTAINER_RUNTIME tag "$SOURCE_TAG" "$TARGET_TAG"

# Detect actual image name in k3s after import (podman may add localhost/ prefix)
detect_k3s_image_name() {
    local base_tag="$1"

    if [ "$CONTAINER_RUNTIME" = "podman" ]; then
        # Check localhost/ prefixed version first
        if k3s ctr images list | grep -q "localhost/${base_tag}"; then
            echo "localhost/${base_tag}"
            return 0
        fi
        # Check non-prefixed version
        if k3s ctr images list | grep -q "^${base_tag}"; then
            echo "${base_tag}"
            return 0
        fi
        return 1
    else
        # Docker doesn't add prefix
        echo "${base_tag}"
        return 0
    fi
}

# Step 2: Export and import to k3s
echo ""
echo -e "${BLUE}[3/4] Importing image to k3s...${NC}"
TEMP_TAR=$(mktemp /tmp/image-XXXXXX.tar)
trap "rm -f $TEMP_TAR" EXIT

echo "Exporting image to $TEMP_TAR..."
$CONTAINER_RUNTIME save -o "$TEMP_TAR" "$TARGET_TAG"

echo "Importing to k3s containerd..."
k3s ctr images import "$TEMP_TAR"

echo "Detecting imported image name..."
K3S_IMAGE_TAG=$(detect_k3s_image_name "$TARGET_TAG")
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Image not found in k3s after import${NC}"
    echo "Expected one of:"
    echo "  - localhost/${TARGET_TAG}"
    echo "  - ${TARGET_TAG}"
    echo ""
    echo "Available images:"
    k3s ctr images list | grep "$IMAGE_NAME"
    exit 1
fi

echo -e "${GREEN}Image imported successfully: $K3S_IMAGE_TAG${NC}"

# Step 3: Update deployment
echo ""
echo -e "${BLUE}[4/4] Updating deployment...${NC}"

DEPLOYMENT_NAME="$RELEASE_NAME-$MODULE"
CONTAINER_NAME="$MODULE"

echo "Deployment: $DEPLOYMENT_NAME"
echo "Container: $CONTAINER_NAME"
echo "New image: $K3S_IMAGE_TAG"

kubectl patch deployment "$DEPLOYMENT_NAME" \
    -n "$NAMESPACE" \
    --type='json' \
    -p="[{\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/image\", \"value\": \"$K3S_IMAGE_TAG\"}]"

echo ""
echo "Waiting for rollout to complete..."
kubectl rollout status deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" --timeout=300s

echo ""
echo -e "${GREEN}=========================================="
echo "  Reload completed successfully!"
echo -e "==========================================${NC}"
echo ""
echo "Deployment: $DEPLOYMENT_NAME"
echo "Image: $K3S_IMAGE_TAG"
echo ""
echo "Check status:"
echo "  kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=$MODULE"
echo ""
