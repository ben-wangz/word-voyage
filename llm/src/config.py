# Configuration for LLM Proxy Service
import os

# Service
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8011"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
