---
name: version-control
description: Manage chart and image versions. Use for version queries, bumping versions.
---

# Version Control

Follows [Semantic Versioning 2.0](https://semver.org/)

## Core Files

| File | Purpose |
|------|---------|
| `frontend/VERSION`, `backend/VERSION`, `llm/VERSION` | Image version source of truth |
| `chart/Chart.yaml` | Chart version, appVersion, and `word-voyage/images` annotation |
| `chart/values.yaml` | Image tags (synced from VERSION files) |

## Scripts

| Script | Purpose |
|--------|---------|
| `tools/version/get-version.sh` | Query all versions |
| `tools/version/bump-image-version.sh` | Bump service image version |
| `tools/version/bump-chart-version.sh` | Bump chart version, optionally sync image tags |

### get-version.sh Usage

```bash
# List all versions
bash tools/version/get-version.sh

# Get chart version
bash tools/version/get-version.sh chart

# Get chart appVersion
bash tools/version/get-version.sh chart app

# Get service image version
bash tools/version/get-version.sh frontend image
bash tools/version/get-version.sh backend image
bash tools/version/get-version.sh llm image
```

## Workflow

1. Bump image versions: `bash tools/version/bump-image-version.sh <service> <major|minor|patch>`
2. Bump chart version with sync: `bash tools/version/bump-chart-version.sh <major|minor|patch> --sync-images`

`--sync-images` reads VERSION files and updates `chart/values.yaml` image tags via `word-voyage/images` annotation mapping.

## Important

**Never bump versions without user confirmation.** When a version bump seems needed, ask the user first before executing any bump script.
