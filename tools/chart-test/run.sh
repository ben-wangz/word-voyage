#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RELEASE_NAME="word-voyage"
NAMESPACE="default"
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"

ensure_helm() {
    if command -v helm &>/dev/null; then
        return 0
    fi
    echo "helm not found, installing..."
    curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    echo "helm installed successfully"
}

usage() {
    echo "Usage: $0 {deploy|undeploy|status}"
    echo ""
    echo "Environment variables (required for deploy):"
    echo "  OPENAI_BASE_URL"
    echo "  OPENAI_API_KEY"
    echo "  OPENAI_MODEL"
    exit 1
}

check_env() {
    local missing=0
    for var in OPENAI_BASE_URL OPENAI_API_KEY OPENAI_MODEL; do
        if [ -z "${!var}" ]; then
            echo "Error: $var is not set"
            missing=1
        fi
    done
    if [ $missing -eq 1 ]; then
        exit 1
    fi
}

cmd_deploy() {
    check_env
    echo "Deploying helm chart..."
    helm upgrade --install "$RELEASE_NAME" "$PROJECT_ROOT/chart" \
        -n "$NAMESPACE" \
        -f "$SCRIPT_DIR/values.yaml" \
        --set credentials.openai.baseUrl="$OPENAI_BASE_URL" \
        --set credentials.openai.apiKey="$OPENAI_API_KEY" \
        --set credentials.openai.model="$OPENAI_MODEL"
    echo "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance="$RELEASE_NAME" -n "$NAMESPACE" --timeout=300s
}

cmd_undeploy() {
    echo "Uninstalling helm chart..."
    helm uninstall "$RELEASE_NAME" -n "$NAMESPACE" || true
}

cmd_status() {
    echo "==> Helm Release"
    helm list -n "$NAMESPACE" | grep "$RELEASE_NAME" || echo "Not deployed"
    echo ""
    echo "==> Pods"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
    echo ""
    echo "==> Services"
    kubectl get svc -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
}

ensure_helm

case "${1:-}" in
    deploy)   cmd_deploy ;;
    undeploy) cmd_undeploy ;;
    status)   cmd_status ;;
    *)        usage ;;
esac
