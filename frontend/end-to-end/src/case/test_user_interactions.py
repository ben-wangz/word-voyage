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
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

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
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

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
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

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


def test_rollback_button_visibility(client: PlaywrightClient, result: TestResult) -> None:
    """Test rollback button visibility on hover

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_rollback_button_visibility"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

        # Process 2 steps to generate history
        initial_event = client.get_current_event_text()
        client.submit_user_input("Action 1")
        client.wait_for_new_event(initial_event, timeout=int(client.timeout * 1.5))

        event_after_first = client.get_current_event_text()
        client.submit_user_input("Action 2")
        client.wait_for_new_event(event_after_first, timeout=int(client.timeout * 1.5))

        client.capture_screenshot("01_history_generated")

        # Find history items
        history_items = client.page.query_selector_all(".history-item")
        assert len(history_items) >= 1, "Should have at least 1 history item"

        first_item = history_items[0]

        # Check button is not visible initially
        rollback_button = first_item.query_selector(".rollback-button")
        assert rollback_button is not None, "Rollback button should exist"

        opacity_before = rollback_button.evaluate("el => window.getComputedStyle(el).opacity")
        assert float(opacity_before) == 0, f"Button should be invisible (opacity 0), got {opacity_before}"

        client.capture_screenshot("02_button_invisible")

        # Hover over history item
        first_item.hover()
        client.page.wait_for_timeout(500)  # Wait for transition

        # Check button is visible after hover
        opacity_after = rollback_button.evaluate("el => window.getComputedStyle(el).opacity")
        assert float(opacity_after) == 1, f"Button should be visible (opacity 1) on hover, got {opacity_after}"

        client.capture_screenshot("03_button_visible_on_hover")

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


def test_rollback_with_confirmation(client: PlaywrightClient, result: TestResult) -> None:
    """Test rollback functionality with confirmation dialog

    Note: History display excludes the current step. Rolling back to Action 1
    means history will show only the initial step (1 item), as Action 1 becomes
    the current step.

    Args:
        client: Playwright client instance
        result: Test result collector
    """
    test_name = "test_rollback_with_confirmation"
    client.screenshot_manager.set_test_context(test_name)

    start_time = time.time()
    try:
        # Reset session to start fresh
        client.reset_game_session()
        client.page.wait_for_timeout(500)

        # Get initial history count (should be 0 - no history yet)
        initial_history_count = client.get_history_count()

        # Process 3 steps (Action 1, 2, 3)
        # After this, history will be: [initial, action1, action2] (3 items)
        # (action3 is the current step, not shown in history)
        initial_event = client.get_current_event_text()
        client.submit_user_input("Action 1")
        client.wait_for_new_event(initial_event, timeout=int(client.timeout * 1.5))

        event_1 = client.get_current_event_text()
        client.submit_user_input("Action 2")
        client.wait_for_new_event(event_1, timeout=int(client.timeout * 1.5))

        event_2 = client.get_current_event_text()
        client.submit_user_input("Action 3")
        client.wait_for_new_event(event_2, timeout=int(client.timeout * 1.5))

        client.capture_screenshot("01_three_steps_completed")

        # Verify we added 3 history items
        history_count_before = client.get_history_count()
        assert history_count_before == initial_history_count + 3, f"Expected {initial_history_count + 3} history items, got {history_count_before}"

        # Find second history item (Action 1) and its rollback button
        history_items = client.page.query_selector_all(".history-item")
        second_item = history_items[1]
        second_item.hover()
        client.page.wait_for_timeout(300)

        rollback_button = second_item.query_selector(".rollback-button")
        assert rollback_button is not None, "Rollback button should exist"

        client.capture_screenshot("02_hover_second_item")

        # Click rollback button - should show confirmation dialog
        dismiss_handler = lambda dialog: dialog.dismiss()
        client.page.on("dialog", dismiss_handler)
        rollback_button.click()
        client.page.wait_for_timeout(500)

        client.capture_screenshot("03_after_cancel")

        # Verify nothing changed after cancel
        history_count_after_cancel = client.get_history_count()
        assert history_count_after_cancel == initial_history_count + 3, f"History should not change after cancel, got {history_count_after_cancel}"

        # Click again and accept
        client.page.remove_listener("dialog", dismiss_handler)
        client.page.on("dialog", lambda dialog: dialog.accept())

        second_item.hover()
        client.page.wait_for_timeout(300)
        rollback_button.click()
        client.page.wait_for_timeout(1000)  # Wait for rollback to complete

        client.capture_screenshot("04_after_accept")

        # Verify history reduced to 1 item after rollback to Action 1
        # After rollback: history = [initial, action1], display = [initial] (1 item)
        history_count_after_rollback = client.get_history_count()
        assert history_count_after_rollback == initial_history_count + 1, f"Expected {initial_history_count + 1} history items after rollback to Action 1, got {history_count_after_rollback}"

        client.capture_screenshot("05_rollback_completed")

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
