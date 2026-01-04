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


# Test case registry
TEST_CASES = [
    {
        "name": "test_game_initialization",
        "function": test_game_initialization,
        "description": "Game initialization"
    },
    {
        "name": "test_single_user_input",
        "function": test_single_user_input,
        "description": "Single user input"
    },
    {
        "name": "test_multiple_sequential_inputs",
        "function": test_multiple_sequential_inputs,
        "description": "Multiple sequential inputs"
    },
    {
        "name": "test_context_update_after_input",
        "function": test_context_update_after_input,
        "description": "Context update after input"
    },
    {
        "name": "test_history_list_updates",
        "function": test_history_list_updates,
        "description": "History list updates"
    },
    {
        "name": "test_event_display_updates",
        "function": test_event_display_updates,
        "description": "Event display updates"
    },
    {
        "name": "test_context_display_structure",
        "function": test_context_display_structure,
        "description": "Context display structure"
    },
    {
        "name": "test_rollback_button_visibility",
        "function": test_rollback_button_visibility,
        "description": "Rollback button visibility"
    },
    {
        "name": "test_rollback_with_confirmation",
        "function": test_rollback_with_confirmation,
        "description": "Rollback with confirmation"
    }
]


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

    # Filter test cases based on selection
    cases_to_run = TEST_CASES
    if Config.SELECTED_CASES:
        selected_names = [name.strip() for name in Config.SELECTED_CASES]
        cases_to_run = [case for case in TEST_CASES if case["name"] in selected_names]

        if not cases_to_run:
            print(f"✗ No matching test cases found for: {', '.join(selected_names)}")
            print(f"\nAvailable test cases:")
            for case in TEST_CASES:
                print(f"  - {case['name']}")
            return False

    try:
        with PlaywrightClient(
            frontend_url=Config.FRONTEND_URL,
            browser_ws_url=Config.BROWSER_WS_URL,
            screenshot_manager=screenshot_manager,
            timeout=Config.PAGE_LOAD_TIMEOUT * 1000
        ) as client:
            print(f"Connected to frontend: {Config.FRONTEND_URL}")
            print(f"Browser WS URL: {Config.BROWSER_WS_URL}")

            # Run selected test cases
            for case in cases_to_run:
                try:
                    case["function"](client, result)
                except Exception as e:
                    print(f"\n{case['description']} test failed: {e}")

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
