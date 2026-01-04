"""Test UI element updates and rendering"""

import time
from ..utils.playwright_client import PlaywrightClient
from ..utils.test_result import TestResult


def test_history_list_updates(client: PlaywrightClient, result: TestResult) -> None:
    """Test that history list properly updates

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_history_list_updates"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

        # Initial state should have 0 history
        initial_count = client.get_history_count()
        client.capture_screenshot("01_initial_history")

        # Perform 3 actions and verify history grows
        for i in range(1, 4):
            previous_event = client.get_current_event_text()
            client.submit_user_input(f"Action {i}")
            client.wait_for_new_event(previous_event, timeout=int(client.timeout * 1.5))

            new_count = client.get_history_count()
            expected_count = initial_count + i
            assert new_count == expected_count, f"History should have {expected_count} entries, found {new_count}"

            client.capture_screenshot(f"02_after_action_{i}")

        client.capture_screenshot("03_final_history")

        duration = time.time() - start_time
        result.add(test_name, "success", duration)

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


def test_event_display_updates(client: PlaywrightClient, result: TestResult) -> None:
    """Test that event display properly updates

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_event_display_updates"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

        events_seen = []

        # Collect several events
        for i in range(3):
            current_event = client.get_current_event_text()
            events_seen.append(current_event)

            assert current_event, f"Event {i+1} should not be empty"
            assert len(current_event) > 10, f"Event {i+1} should have meaningful content"

            client.capture_screenshot(f"0{i+1}_event_{i+1}")

            if i < 2:  # Don't submit after last event
                client.submit_user_input(f"Continue {i+1}")
                client.wait_for_new_event(current_event, timeout=int(client.timeout * 1.5))

        # Verify events were different (not all identical)
        unique_events = set(events_seen)
        assert len(unique_events) > 1, "Should have different events, not all identical"

        client.capture_screenshot("04_final_state")

        duration = time.time() - start_time
        result.add(test_name, "success", duration)

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


def test_context_display_structure(client: PlaywrightClient, result: TestResult) -> None:
    """Test context display has proper structure

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_context_display_structure"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

        client.capture_screenshot("01_context_display")

        context = client.get_context_state()

        # Verify context is present and structured
        assert context, "Context should not be empty"
        assert isinstance(context, dict), "Context should be a dictionary"
        assert len(context) > 0, "Context should have at least one field"

        # Verify all values are reasonable types
        for key, value in context.items():
            assert isinstance(key, str), f"Key should be string: {key}"
            assert value is not None, f"Value for {key} should not be None"
            # Values should be numbers or strings
            assert isinstance(value, (int, float, str)), f"Value for {key} should be int, float, or str, got {type(value)}"

        client.capture_screenshot("02_context_verified")

        duration = time.time() - start_time
        result.add(test_name, "success", duration)

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
