#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

IMAGE="quay.io/helmpack/chart-testing:v3.13.0"

podman run --rm \
    -v "$PROJECT_ROOT:/workdir" \
    -w /workdir \
    "$IMAGE" \
    ct lint --config /workdir/tools/chart-lint/ct.yaml --charts /workdir/chart
