# WordVoyage

An AI-powered text-based sandbox game where your words shape the journey.

## Core Concept
Type to interact, AI to generate—explore infinite, dynamic worlds driven by natural language. No limits, just text and adventure.

## Key Features
- AI-generated scenes & narratives (LLM-powered)
- Open-world text sandbox (free-form exploration)
- Text-only interaction (simple, immersive input)

## Quick Start

Install WordVoyage using Helm:

```bash
# Get the latest chart version
CHART_VERSION=$(bash tools/version/get-version.sh chart)

# Install with Helm
helm upgrade --install word-voyage \
  oci://ghcr.io/ben-wangz/word-voyage-charts/word-voyage \
  --version ${CHART_VERSION} \
  --namespace word-voyage \
  --create-namespace \
  --set credentials.openai.baseUrl="your-openai-base-url" \
  --set credentials.openai.apiKey="your-openai-api-key" \
  --set credentials.openai.model="your-openai-model"
```

## Version Control

See [.claude/skills/version-control/SKILL.md](.claude/skills/version-control/SKILL.md)

## Local Tests

See [.claude/skills/local-tests/SKILL.md](.claude/skills/local-tests/SKILL.md)

## Helm Chart Lint

See [.claude/skills/chart-lint/SKILL.md](.claude/skills/chart-lint/SKILL.md)

## Helm Chart Test

See [.claude/skills/chart-test/SKILL.md](.claude/skills/chart-test/SKILL.md)

## Contributing
PRs & issues are welcome! Feel free to propose features or report bugs.

## License
Custom MIT License
Copyright (c) 2025 [ben.wangz@foxmail.com]
This software is provided under a custom MIT License that requires it to be distributed as free software to end users.
See the LICENSE file for full license text.
