---
name: local-tests
description: Run local end-to-end tests for each module. Use for testing LLM, backend, frontend services.
---

# Local Tests

## Environment Variables

Required variables (provide or load from `.env`):

```bash
export OPENAI_BASE_URL=<your-openai-base-url>
export OPENAI_API_KEY=<your-openai-api-key>
export OPENAI_MODEL=<your-openai-model-name>
```

Optional:

| Variable | Description |
|----------|-------------|
| `BUILD_ARG_PIP_INDEX_URL` | PyPI mirror URL (e.g., `https://mirrors.aliyun.com/pypi/simple/`) |

## Test Commands

### LLM Module

```bash
SERVICE_OPENAI_BASE_URL=$OPENAI_BASE_URL \
SERVICE_OPENAI_API_KEY=$OPENAI_API_KEY \
SERVICE_OPENAI_MODEL=$OPENAI_MODEL \
llm/end-to-end/test.sh
```

### Backend Module

1. Start Redis: `middlewares/redis.sh start`
2. Start LLM service:
   ```bash
   SERVICE_OPENAI_BASE_URL=$OPENAI_BASE_URL \
   SERVICE_OPENAI_API_KEY=$OPENAI_API_KEY \
   SERVICE_OPENAI_MODEL=$OPENAI_MODEL \
   tools/deploy.sh llm --action start --build
   ```
3. Run tests: `backend/end-to-end/test.sh`

### Frontend Module

1. Start Redis: `middlewares/redis.sh start`
2. Start LLM service:
   ```bash
   SERVICE_OPENAI_BASE_URL=$OPENAI_BASE_URL \
   SERVICE_OPENAI_API_KEY=$OPENAI_API_KEY \
   SERVICE_OPENAI_MODEL=$OPENAI_MODEL \
   tools/deploy.sh llm --action start --build
   ```
3. Start Backend service: `tools/deploy.sh backend --action start --build`
4. Run tests: `frontend/end-to-end/test.sh`

## Dependencies

- LLM: standalone, no dependencies
- Backend: requires LLM and Redis
- Frontend: requires Backend and LLM (and transitively Redis)

## Cleanup

Stop services after testing:
```bash
tools/deploy.sh llm --action stop
tools/deploy.sh backend --action stop
middlewares/redis.sh stop
```

## Quick Test All Modules

```bash
# Start dependencies
middlewares/redis.sh start
SERVICE_OPENAI_BASE_URL=$OPENAI_BASE_URL \
SERVICE_OPENAI_API_KEY=$OPENAI_API_KEY \
SERVICE_OPENAI_MODEL=$OPENAI_MODEL \
tools/deploy.sh llm --action start --build

# Test LLM
SERVICE_OPENAI_BASE_URL=$OPENAI_BASE_URL \
SERVICE_OPENAI_API_KEY=$OPENAI_API_KEY \
SERVICE_OPENAI_MODEL=$OPENAI_MODEL \
llm/end-to-end/test.sh

# Test Backend
tools/deploy.sh backend --action start --build
backend/end-to-end/test.sh

# Test Frontend
frontend/end-to-end/test.sh

# Cleanup
tools/deploy.sh llm --action stop
tools/deploy.sh backend --action stop
middlewares/redis.sh stop
```

## Pre-flight Check

Before running tests, ensure required variables are set:

```bash
if [ -z "$OPENAI_BASE_URL" ] || [ -z "$OPENAI_API_KEY" ] || [ -z "$OPENAI_MODEL" ]; then
  echo "Error: Missing required environment variables"
  echo "Set: OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL"
  exit 1
fi
```

## Important

**Always ask before running tests.** Tests may take time and consume resources.
**Always verify required environment variables are set before executing any test command.**
