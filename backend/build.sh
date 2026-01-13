#!/bin/bash

# ==========================================
# WordVoyage Backend - Build Script (Wrapper)
# ==========================================
#
# This script wraps tools/build.sh for backward compatibility.
# All arguments are passed through to the unified build script.
#
# Usage:
#   ./build.sh [--push]
#
# Environment Variables:
#   IMAGE_NAME    Override image name
#   VERSION       Override version
#   BUILD_ARG_*   Pass build arguments to container build

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../tools/build.sh" backend "$@"
