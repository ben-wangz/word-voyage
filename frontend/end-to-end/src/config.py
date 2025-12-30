"""Configuration management for frontend end-to-end tests"""

import os
import sys
from pathlib import Path


class Config:
    """Test configuration"""

    # Service URLs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://host.containers.internal:3000")
    BROWSER_WS_URL = os.getenv("BROWSER_WS_URL", "ws://host.containers.internal:3003/chromium/playwright?headless=true")
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "/app/screenshots")

    # Timeouts (in seconds)
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "15"))
    WAIT_FOR_EVENT_TIMEOUT = int(os.getenv("WAIT_FOR_EVENT_TIMEOUT", "10"))

    # Browser settings
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate configuration

        Raises:
            ValueError: If configuration is invalid
        """
        # Check screenshot directory is writable
        try:
            Path(cls.SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Screenshot directory not writable: {cls.SCREENSHOT_DIR}") from e

    @classmethod
    def display(cls) -> None:
        """Display configuration"""
        print("\n" + "="*60)
        print("Frontend E2E Test Configuration")
        print("="*60)
        print(f"Frontend URL:         {cls.FRONTEND_URL}")
        print(f"Browser WS URL:       {cls.BROWSER_WS_URL}")
        print(f"Screenshot Dir:       {cls.SCREENSHOT_DIR}")
        print(f"Test Timeout:         {cls.TEST_TIMEOUT}s")
        print(f"Page Load Timeout:    {cls.PAGE_LOAD_TIMEOUT}s")
        print(f"Event Wait Timeout:   {cls.WAIT_FOR_EVENT_TIMEOUT}s")
        print(f"Headless Mode:        {cls.HEADLESS}")
        print("="*60 + "\n")
