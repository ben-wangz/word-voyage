"""Screenshot management and organization"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class ScreenshotManager:
    """Manages screenshot capture and organization"""

    def __init__(self, base_dir: str):
        """Initialize screenshot manager

        Args:
            base_dir: Base directory for screenshots
        """
        self.base_dir = Path(base_dir)
        self.run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_dir = self.base_dir / self.run_timestamp
        self.current_test_dir: Optional[Path] = None

        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def set_test_context(self, test_name: str) -> None:
        """Set current test context for screenshot organization

        Args:
            test_name: Name of current test case
        """
        self.current_test_dir = self.run_dir / test_name
        self.current_test_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, page, step_name: str) -> str:
        """Capture screenshot and save

        Args:
            page: Playwright page object
            step_name: Name of the step for file naming

        Returns:
            Relative path to saved screenshot
        """
        if not self.current_test_dir:
            raise RuntimeError("Test context not set. Call set_test_context() first.")

        # Generate filename with sequential numbering
        existing_files = list(self.current_test_dir.glob("*.png"))
        sequence = len(existing_files) + 1
        filename = f"{sequence:02d}_{step_name}.png"
        filepath = self.current_test_dir / filename

        # Capture screenshot
        page.screenshot(path=str(filepath))

        # Return relative path for logging
        relative_path = f"{self.run_timestamp}/{self.current_test_dir.name}/{filename}"
        return relative_path

    def get_run_dir(self) -> str:
        """Get current run directory

        Returns:
            Path to current run directory
        """
        return str(self.run_dir)

    def get_test_dir(self) -> Optional[str]:
        """Get current test directory

        Returns:
            Path to current test directory or None
        """
        return str(self.current_test_dir) if self.current_test_dir else None
