"""Configuration for end-to-end tests"""

import os


class Config:
    """Test configuration"""

    # Service endpoint
    SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://host.containers.internal:8011")

    # Test context limits
    CONTEXT_MAX_FIELDS = 16

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.SERVICE_URL:
            raise ValueError("LLM_SERVICE_URL must be set")

    @classmethod
    def display(cls):
        """Display configuration"""
        print("=" * 50)
        print("Test Configuration")
        print("=" * 50)
        print(f"Service URL: {cls.SERVICE_URL}")
        print(f"Context Max Fields: {cls.CONTEXT_MAX_FIELDS}")
        print("=" * 50)
        print()
