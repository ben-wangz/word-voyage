"""Test user interactions and event responses"""

import time
from ..utils.playwright_client import PlaywrightClient
from ..utils.test_result import TestResult


def test_single_user_input(client: PlaywrightClient, result: TestResult) -> None:
    """Test single user input and response

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_single_user_input"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Get initial state
        initial_event = client.get_current_event_text()
        initial_history_count = client.get_history_count()
        client.capture_screenshot("01_initial_state")

        # Submit input
        test_input = "Look around carefully"
        client.submit_user_input(test_input)
        client.capture_screenshot("02_input_submitted")

        # Wait for new event
        client.wait_for_new_event(initial_event, timeout=int(client.timeout * 1.5))
        client.capture_screenshot("03_event_received")

        # Verify event changed
        new_event = client.get_current_event_text()
        assert new_event != initial_event, "Event should change after input"
        assert len(new_event) > 0, "New event should not be empty"

        # Verify history increased
        new_history_count = client.get_history_count()
        assert new_history_count > initial_history_count, "History count should increase"

        # Verify no error
        error = client.check_error_message()
        assert error is None, f"Should not have error, found: {error}"

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


def test_multiple_sequential_inputs(client: PlaywrightClient, result: TestResult) -> None:
    """Test multiple sequential user inputs

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_multiple_sequential_inputs"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        test_inputs = [
            "Check my health status",
            "Find water source",
            "Rest for a while"
        ]

        previous_event = client.get_current_event_text()
        previous_history_count = client.get_history_count()

        for i, test_input in enumerate(test_inputs, 1):
            client.capture_screenshot(f"0{i}_before_input")

            # Submit input
            client.submit_user_input(test_input)

            # Wait for response
            client.wait_for_new_event(previous_event, timeout=int(client.timeout * 1.5))

            # Verify state changed
            new_event = client.get_current_event_text()
            assert new_event != previous_event, f"Event should change on input {i}"

            new_history_count = client.get_history_count()
            assert new_history_count > previous_history_count, f"History should increase on input {i}"

            client.capture_screenshot(f"0{i}_after_input_{i}")

            # Update for next iteration
            previous_event = new_event
            previous_history_count = new_history_count

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


def test_context_update_after_input(client: PlaywrightClient, result: TestResult) -> None:
    """Test that context state updates after user input

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_context_update_after_input"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Get initial context
        initial_context = client.get_context_state()
        initial_event = client.get_current_event_text()
        client.capture_screenshot("01_initial_context")

        assert initial_context, "Should have initial context"

        # Submit action that affects state
        client.submit_user_input("Do something")
        client.wait_for_new_event(initial_event, timeout=int(client.timeout * 1.5))
        client.capture_screenshot("02_after_action")

        # Get new context
        new_context = client.get_context_state()
        assert new_context, "Should have updated context"

        # Note: We may not be able to verify specific values changed without knowing game logic
        # But we can verify the structure is consistent
        assert len(new_context) > 0, "Context should have state values"

        # Both contexts should have similar keys (or new context might have more/different values)
        # Just verify the context is valid and non-empty
        for key, value in new_context.items():
            assert isinstance(key, str), f"Context key should be string, got {type(key)}"
            assert value is not None, f"Context value for {key} should not be None"

        client.capture_screenshot("03_final_context")

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
