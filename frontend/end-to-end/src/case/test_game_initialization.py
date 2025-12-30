"""Test game initialization and page load"""

import time
from ..utils.playwright_client import PlaywrightClient
from ..utils.test_result import TestResult


def test_game_initialization(client: PlaywrightClient, result: TestResult) -> None:
    """Test game page initialization and loading

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_game_initialization"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Navigate to game page
        client.navigate_to_game()
        client.screenshot_manager.capture(client.page, "01_page_load_start")

        # Wait for page to be ready
        client.wait_for_game_ready()
        screenshot_ready = client.capture_screenshot("02_page_ready")

        # Verify event description is present
        event_text = client.get_current_event_text()
        assert event_text, "Event description should not be empty"
        assert len(event_text) > 10, "Event description should have meaningful content"

        # Verify context state is displayed
        context = client.get_context_state()
        assert context, "Context state should not be empty"
        assert len(context) > 0, "Should have at least one state value"

        # Verify input form is accessible
        input_field = client.page.query_selector("input[type='text'], textarea")
        assert input_field, "Input field should be present"
        assert input_field.is_enabled(), "Input field should be enabled"

        # Verify history is empty on initialization
        history_count = client.get_history_count()
        assert history_count == 0, f"History should be empty on init, found {history_count} entries"

        # Verify no error messages
        error = client.check_error_message()
        assert error is None, f"Should not have error messages, found: {error}"

        client.capture_screenshot("03_final_state")

        duration = time.time() - start_time
        result.add(test_name, "success", duration, screenshot=screenshot_ready)

    except AssertionError as e:
        duration = time.time() - start_time
        try:
            screenshot = client.capture_screenshot("error_state")
        except:
            screenshot = None
        result.add(test_name, "failed", duration, str(e), screenshot)
        raise

    except Exception as e:
        duration = time.time() - start_time
        try:
            screenshot = client.capture_screenshot("error_state")
        except:
            screenshot = None
        result.add(test_name, "failed", duration, str(e), screenshot)
        raise
