#!/bin/bash

set -o errexit -o nounset -o pipefail

# Script to get version information for word-voyage services
# Usage:
#   bash get-version.sh                    # List all versions
#   bash get-version.sh <service-name> [image|chart]
#
# Examples:
#   bash get-version.sh                   # List all chart and image versions
#   bash get-version.sh frontend image
#   bash get-version.sh backend image
#   bash get-version.sh chart

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

function usage() {
    echo "Usage: $0 [service-name] [image|chart]"
    echo ""
    echo "Get version information for services or list all versions"
    echo ""
    echo "Arguments:"
    echo "  (no args)     List all chart and image versions"
    echo "  service-name  Service name (frontend, backend, llm) or 'chart'"
    echo "  type          Version type: 'image' or 'chart' (default: chart)"
    echo ""
    echo "Examples:"
    echo "  $0                    # List all versions"
    echo "  $0 frontend image     # Get frontend image version"
    echo "  $0 backend image      # Get backend image version"
    echo "  $0 chart              # Get helm chart version"
    exit 1
}

function list_all_versions() {
    echo "=== Helm Chart ==="
    echo ""

    local chart_file="${PROJECT_ROOT}/chart/Chart.yaml"
    if [[ -f "$chart_file" ]]; then
        local version=$(grep '^version:' "$chart_file" | awk '{print $2}')
        local app_version=$(grep '^appVersion:' "$chart_file" | awk '{print $2}' | tr -d '"')
        printf "  %-20s chart: %-10s appVersion: %s\\n" "word-voyage" "$version" "$app_version"
    fi

    echo ""
    echo "=== Service Images ==="
    echo ""

    # List all service VERSION files
    for service_dir in "${PROJECT_ROOT}"/{frontend,backend,llm}; do
        if [[ -d "$service_dir" ]] && [[ -f "${service_dir}/VERSION" ]]; then
            local service_name=$(basename "$service_dir")
            local version=$(cat "${service_dir}/VERSION")
            printf "  %-20s image: %s\\n" "$service_name" "$version"
        fi
    done

    echo ""
}

function get_image_version() {
    local service_name="$1"
    local version_file="${PROJECT_ROOT}/${service_name}/VERSION"

    if [[ ! -f "${version_file}" ]]; then
        echo "Error: VERSION file not found at ${version_file}" >&2
        exit 1
    fi

    cat "${version_file}"
}

function get_chart_version() {
    local chart_file="${PROJECT_ROOT}/chart/Chart.yaml"

    if [[ ! -f "${chart_file}" ]]; then
        echo "Error: Chart.yaml not found at ${chart_file}" >&2
        exit 1
    fi

    grep '^version:' "${chart_file}" | awk '{print $2}'
}

function get_app_version() {
    local chart_file="${PROJECT_ROOT}/chart/Chart.yaml"

    if [[ ! -f "${chart_file}" ]]; then
        echo "Error: Chart.yaml not found at ${chart_file}" >&2
        exit 1
    fi

    grep '^appVersion:' "${chart_file}" | awk '{print $2}' | tr -d '"'
}

# Main
if [[ $# -eq 0 ]]; then
    # No arguments: list all versions
    list_all_versions
    exit 0
elif [[ $# -gt 2 ]]; then
    usage
fi

SERVICE_NAME="$1"
VERSION_TYPE="${2:-chart}"

# Handle 'chart' as a special case
if [[ "$SERVICE_NAME" == "chart" ]]; then
    if [[ "$VERSION_TYPE" == "chart" ]]; then
        get_chart_version
    elif [[ "$VERSION_TYPE" == "app" ]] || [[ "$VERSION_TYPE" == "appVersion" ]]; then
        get_app_version
    else
        echo "Error: For 'chart', type must be 'chart' or 'app'" >&2
        usage
    fi
    exit 0
fi

case "${VERSION_TYPE}" in
    image)
        get_image_version "${SERVICE_NAME}"
        ;;
    chart)
        get_chart_version
        ;;
    app|appVersion)
        get_app_version
        ;;
    *)
        echo "Error: Invalid version type '${VERSION_TYPE}'. Must be 'image' or 'chart'" >&2
        usage
        ;;
esac
