---
name: chart-lint
description: Lint Helm chart using chart-testing. Use for validating chart syntax and structure.
---

# Helm Chart Lint

## Overview

Uses [chart-testing](https://github.com/helm/chart-testing) (`ct lint`) to validate Helm chart syntax and structure.

## Requirements

- Podman

## Run Lint

```bash
tools/chart-lint/run.sh
```

## What It Checks

- Chart.yaml structure and required fields
- YAML syntax validation (yamllint)
- Helm template rendering
- Values schema validation

## Configuration

Config file: `tools/chart-lint/ct.yaml`

## Expected Output

```
==> Linting /workdir/chart
...

1 chart(s) linted, 0 chart(s) failed
```

## Important

**Always ask before running lint.** The command pulls a container image on first run.
