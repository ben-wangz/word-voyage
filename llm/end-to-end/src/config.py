"""Configuration for OpenAI LLM E2E tests"""

import os


class Config:
    """Configuration from environment variables"""

    # OpenAI LLM Service
    SERVICE_URL = os.getenv("SERVICE_URL", "http://host.containers.internal:8011")

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = {
            "SERVICE_URL": cls.SERVICE_URL,
        }

        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    @classmethod
    def display(cls):
        """Display configuration (safe)"""
        print("Configuration:")
        print(f"  Service URL: {cls.SERVICE_URL}")
        print()