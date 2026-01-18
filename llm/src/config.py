# Configuration for LLM Proxy Service
import os

# Service
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8011"))

# OpenAI API
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate required configuration
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required but not set")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
