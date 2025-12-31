"""Playwright client for WordVoyage frontend testing"""

from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, Page, Browser, Playwright
from .screenshot_manager import ScreenshotManager


class PlaywrightClient:
    """Client for WordVoyage frontend browser automation"""

    def __init__(
        self,
        frontend_url: str,
        browser_ws_url: str,
        screenshot_manager: ScreenshotManager,
        timeout: int = 15000
    ):
        """Initialize client

        Args:
            frontend_url: Frontend application URL
            browser_ws_url: Browserless WebSocket URL
            screenshot_manager: Screenshot manager instance
            timeout: Default timeout in milliseconds
        """
        self.frontend_url = frontend_url.rstrip("/")
        self.browser_ws_url = browser_ws_url
        self.screenshot_manager = screenshot_manager
        self.timeout = timeout

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self) -> None:
        """Connect to remote browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(self.browser_ws_url)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(self.timeout)

    def close(self) -> None:
        """Close browser connection"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def navigate_to_game(self) -> None:
        """Navigate to game page"""
        self.page.goto(self.frontend_url)

    def wait_for_game_ready(self) -> None:
        """Wait for game page to be ready

        Waits for:
        - Event display area
        - Input form
        - Context display
        """
        # Wait for main components to load
        self.page.wait_for_selector("[data-testid='event-display'], .event-display, h2:has-text('Current Event')", timeout=self.timeout)
        self.page.wait_for_selector("input[type='text'], textarea", timeout=self.timeout)
        self.page.wait_for_selector("[data-testid='context-display'], .context-display, h3:has-text('Game State')", timeout=self.timeout)

        # Wait for network to be idle
        self.page.wait_for_load_state('networkidle', timeout=self.timeout)

    def get_current_event_text(self) -> str:
        """Get current event description

        Returns:
            Event description text
        """
        # Try multiple selectors for event text
        selectors = [
            "[data-testid='event-description']",
            ".event-description",
            ".event-display p",
            "main p"
        ]

        for selector in selectors:
            try:
                element = self.page.query_selector(selector)
                if element:
                    text = element.inner_text()
                    if text.strip():
                        return text.strip()
            except:
                continue

        # Fallback: get any paragraph text
        paragraphs = self.page.query_selector_all("p")
        for p in paragraphs:
            text = p.inner_text().strip()
            if text and len(text) > 10:  # Assume event text is longer than 10 chars
                return text

        raise RuntimeError("Could not find event description")

    def get_context_state(self) -> Dict[str, Any]:
        """Get current game state from context display

        Returns:
            Dictionary with state values (health, hunger, etc.)
        """
        context = {}

        # Try to find state display elements
        # Look for patterns like "Health: 100" or "health: 100"
        state_elements = self.page.query_selector_all("[data-testid='context-display'] div, .context-display div, aside div")

        for element in state_elements:
            text = element.inner_text().strip()
            if ":" in text:
                key, value = text.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                # Try to convert to number if possible
                try:
                    if "." in value:
                        context[key] = float(value)
                    else:
                        context[key] = int(value)
                except ValueError:
                    context[key] = value

        return context

    def get_history_count(self) -> int:
        """Get number of history entries

        Returns:
            Number of history entries
        """
        # Try to find history list items
        selectors = [
            "[data-testid='history-item']",
            ".history-item",
            "[data-testid='event-history'] li",
            ".event-history li"
        ]

        for selector in selectors:
            try:
                items = self.page.query_selector_all(selector)
                if items:
                    return len(items)
            except:
                continue

        return 0

    def submit_user_input(self, text: str) -> None:
        """Submit user input text

        Args:
            text: Input text to submit
        """
        # Find input field
        input_selector = "input[type='text'], textarea"
        input_field = self.page.wait_for_selector(input_selector, timeout=self.timeout)

        # Type (fill automatically clears existing text)
        input_field.fill(text)

        # Submit (try multiple methods)
        # Method 1: Press Enter
        try:
            input_field.press("Enter")
            return
        except:
            pass

        # Method 2: Click submit button
        button_selectors = [
            "button[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Send')",
            "form button"
        ]

        for selector in button_selectors:
            try:
                button = self.page.query_selector(selector)
                if button:
                    button.click()
                    return
            except:
                continue

        raise RuntimeError("Could not submit input")

    def wait_for_new_event(self, previous_event_text: str, timeout: int = None) -> None:
        """Wait for a new event to appear

        Args:
            previous_event_text: Previous event text to compare against
            timeout: Timeout in milliseconds (uses default if None)

        Raises:
            TimeoutError: If new event doesn't appear in time
        """
        if timeout is None:
            timeout = self.timeout

        # Poll for event text change
        import time
        start_time = time.time()
        timeout_seconds = timeout / 1000

        while time.time() - start_time < timeout_seconds:
            try:
                current_text = self.get_current_event_text()
                if current_text != previous_event_text:
                    return
            except Exception as e:
                # Log the exception for debugging but continue polling
                pass

            time.sleep(0.5)

        raise TimeoutError(f"New event did not appear within {timeout}ms")

    def check_error_message(self) -> Optional[str]:
        """Check for error messages on page

        Returns:
            Error message text if found, None otherwise
        """
        error_selectors = [
            "[data-testid='error-message']",
            ".error-message",
            ".error",
            "[role='alert']"
        ]

        for selector in error_selectors:
            try:
                element = self.page.query_selector(selector)
                if element and element.is_visible():
                    return element.inner_text().strip()
            except:
                continue

        return None

    def capture_screenshot(self, name: str) -> str:
        """Capture screenshot using screenshot manager

        Args:
            name: Name/description of the screenshot

        Returns:
            Path to saved screenshot
        """
        return self.screenshot_manager.capture(self.page, name)

    def wait_for_loading_complete(self, timeout: int = None) -> None:
        """Wait for loading indicators to disappear

        Args:
            timeout: Timeout in milliseconds (uses default if None)
        """
        if timeout is None:
            timeout = self.timeout

        loading_selectors = [
            "[data-testid='loading']",
            ".loading",
            ".spinner"
        ]

        for selector in loading_selectors:
            try:
                # Wait for element to be hidden or not present
                self.page.wait_for_selector(selector, state="hidden", timeout=1000)
            except:
                pass  # Ignore if selector not found
