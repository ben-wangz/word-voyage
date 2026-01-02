#!/usr/bin/env python3
"""
Main test runner for WordVoyage Frontend end-to-end tests

Runs all test suites and reports results.
"""

import sys
import argparse
from .config import Config
from .utils.playwright_client import PlaywrightClient
from .utils.screenshot_manager import ScreenshotManager
from .utils.test_result import TestResult
from .case.test_game_initialization import test_game_initialization
from .case.test_user_interactions import (
    test_single_user_input,
    test_multiple_sequential_inputs,
    test_context_update_after_input,
    test_rollback_button_visibility,
    test_rollback_with_confirmation
)
from .case.test_ui_updates import (
    test_history_list_updates,
    test_event_display_updates,
    test_context_display_structure
)


def run_all_tests(frontend_url: str = None, browser_ws_url: str = None) -> bool:
    """Run all test suites

    Args:
        frontend_url: Frontend service URL (defaults to Config.FRONTEND_URL)
        browser_ws_url: Browser WebSocket URL (defaults to Config.BROWSER_WS_URL)

    Returns:
        True if all tests passed, False otherwise
    """
    # Use provided URLs or fall back to config
    if frontend_url:
        Config.FRONTEND_URL = frontend_url
    if browser_ws_url:
        Config.BROWSER_WS_URL = browser_ws_url

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False

    # Display configuration
    Config.display()

    # Initialize screenshot manager
    screenshot_manager = ScreenshotManager(Config.SCREENSHOT_DIR)

    result = TestResult()

    try:
        with PlaywrightClient(
            frontend_url=Config.FRONTEND_URL,
            browser_ws_url=Config.BROWSER_WS_URL,
            screenshot_manager=screenshot_manager,
            timeout=Config.PAGE_LOAD_TIMEOUT * 1000
        ) as client:
            print(f"Connected to frontend: {Config.FRONTEND_URL}")
            print(f"Browser WS URL: {Config.BROWSER_WS_URL}")

            # Test 1: Game initialization
            try:
                test_game_initialization(client, result)
            except Exception as e:
                print(f"\nGame initialization test failed: {e}")

            # Test 2: Single user input
            try:
                test_single_user_input(client, result)
            except Exception as e:
                print(f"\nSingle user input test failed: {e}")

            # Test 3: Multiple sequential inputs
            try:
                test_multiple_sequential_inputs(client, result)
            except Exception as e:
                print(f"\nMultiple sequential inputs test failed: {e}")

            # Test 4: Context update after input
            try:
                test_context_update_after_input(client, result)
            except Exception as e:
                print(f"\nContext update test failed: {e}")

            # Test 5: History list updates
            try:
                test_history_list_updates(client, result)
            except Exception as e:
                print(f"\nHistory list updates test failed: {e}")

            # Test 6: Event display updates
            try:
                test_event_display_updates(client, result)
            except Exception as e:
                print(f"\nEvent display updates test failed: {e}")

            # Test 7: Context display structure
            try:
                test_context_display_structure(client, result)
            except Exception as e:
                print(f"\nContext display structure test failed: {e}")

            # Test 8: Rollback button visibility
            try:
                test_rollback_button_visibility(client, result)
            except Exception as e:
                print(f"\nRollback button visibility test failed: {e}")

            # Test 9: Rollback with confirmation
            try:
                test_rollback_with_confirmation(client, result)
            except Exception as e:
                print(f"\nRollback with confirmation test failed: {e}")

    except ConnectionError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTip: Ensure Frontend and Browserless services are running")
        return False

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Always print summary
        result.print_summary()

    # Check if all tests passed
    failed_count = sum(1 for r in result.results if r["status"] == "failed")
    return failed_count == 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="WordVoyage Frontend End-to-End Tests"
    )
    parser.add_argument(
        "--frontend-url",
        default=None,
        help=f"Frontend service URL (default: {Config.FRONTEND_URL})"
    )
    parser.add_argument(
        "--browser-ws-url",
        default=None,
        help=f"Browser WebSocket URL (default: {Config.BROWSER_WS_URL})"
    )

    args = parser.parse_args()

    success = run_all_tests(
        frontend_url=args.frontend_url,
        browser_ws_url=args.browser_ws_url
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
