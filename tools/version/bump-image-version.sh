#!/bin/bash

set -o errexit -o nounset -o pipefail

# Script to bump container image versions
# Usage:
#   bash bump-image-version.sh <service-name> <major|minor|patch>
#
# Examples:
#   bash bump-image-version.sh frontend patch
#   bash bump-image-version.sh backend minor
#   bash bump-image-version.sh llm major

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load version utilities library
source "${SCRIPT_DIR}/lib/version-utils.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function usage() {
    cat << EOF
Usage: $0 <service-name> <bump-type>

Bump container image version following semver.

Arguments:
  service-name  Service name (frontend, backend, llm)
  bump-type     Version bump type: major, minor, or patch

Examples:
  $0 frontend patch    # 1.0.0 -> 1.0.1
  $0 backend minor     # 1.0.0 -> 1.1.0
  $0 llm major         # 1.0.0 -> 2.0.0

EOF
    exit 1
}

# Main
if [[ $# -ne 2 ]]; then
    usage
fi

SERVICE_NAME="$1"
BUMP_TYPE="$2"

log_info "Bumping image version for: $SERVICE_NAME"

# Get version file path
VERSION_FILE=$(resolve_version_file_path "$SERVICE_NAME" "$PROJECT_ROOT")
log_info "VERSION file: $VERSION_FILE"

# Validate file exists
if ! validate_file_exists "$VERSION_FILE" "VERSION"; then
    exit 1
fi

# Read current version
CURRENT_VERSION=$(cat "$VERSION_FILE")
log_info "Current version: $CURRENT_VERSION"

# Calculate new version
if ! NEW_VERSION=$(bump_semver "$CURRENT_VERSION" "$BUMP_TYPE"); then
    log_error "Failed to calculate new version"
    exit 1
fi
log_info "New version: $NEW_VERSION"

# Update VERSION file
echo "$NEW_VERSION" > "$VERSION_FILE"
log_info "Updated $VERSION_FILE"

echo ""
log_info "Version bump complete!"
log_info "  $SERVICE_NAME: $CURRENT_VERSION -> $NEW_VERSION"
echo ""
log_warn "Next steps:"
log_warn "  1. Review the changes"
log_warn "  2. Update the chart version if needed: bash tools/version/bump-chart-version.sh <bump-type> --sync-images"
log_warn "  3. Commit the changes"
