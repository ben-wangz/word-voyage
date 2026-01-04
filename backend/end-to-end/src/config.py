"""Configuration for WordVoyage Backend E2E tests"""

import os


class Config:
    """Configuration from environment variables"""

    # Backend Service
    SERVICE_URL = os.getenv("SERVICE_URL", "http://host.containers.internal:8080")

    # Test case selection
    SELECTED_CASES = os.getenv("SELECTED_CASES", "").split(",") if os.getenv("SELECTED_CASES") else None

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
        if cls.SELECTED_CASES:
            print(f"  Selected Cases: {', '.join(cls.SELECTED_CASES)}")
        else:
            print(f"  Selected Cases: All")
        print()
