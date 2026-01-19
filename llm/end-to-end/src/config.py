"""Configuration for end-to-end tests"""

import os


class Config:
    """Test configuration"""

    # Service endpoint
    SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://host.containers.internal:8011")

    # Test case selection
    SELECTED_CASES = os.getenv("SELECTED_CASES", "").split(",") if os.getenv("SELECTED_CASES") else None

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
        if cls.SELECTED_CASES:
            print(f"Selected Cases: {', '.join(cls.SELECTED_CASES)}")
        else:
            print(f"Selected Cases: All")
        print("=" * 50)
        print()
