# Configuration for OpenAI Service
import os

# Service
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8011"))

# OpenAI API
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Validate required configuration
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required but not set")

# Context limits
CONTEXT_MAX_FIELDS = int(os.getenv("CONTEXT_MAX_FIELDS", "16"))

# LLM generation parameters
# max_tokens: Maximum tokens for LLM output (events + context changes)
# Estimated: event description (100-200 tokens) + context_changes (200-400 tokens) = 500-1500 tokens
# Setting to 3000 for safety margin
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "3000"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")