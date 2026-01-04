#!/usr/bin/env python3
"""
Main test runner for WordVoyage Backend end-to-end tests

Runs all test suites and reports results.
"""

import sys
import argparse
from .config import Config
from .utils.backend_client import BackendGameClient
from .utils.test_result import TestResult
from .case.test_health import test_health_check
from .case.test_game_init import test_start_game
from .case.test_game_step import (
    test_process_action_step,
    test_context_changes_over_steps,
    test_multiple_steps_sequential
)
from .case.test_session_history import (
    test_get_current_context,
    test_get_step_history,
    test_session_isolation,
    test_rollback_to_step,
    test_rollback_invalid_index
)
from .case.test_error_handling import (
    test_invalid_session,
    test_missing_input
)
from .case.test_i18n import test_game_init_i18n
from .case.test_auth import (
    test_anonymous_to_registered,
    test_user_login,
    test_logout,
    test_token_refresh,
    test_cross_user_session_access,
    test_anonymous_session_isolation,
    test_register_preserves_ownership,
    test_invalid_credentials,
    test_duplicate_email,
    test_empty_password,
    test_malformed_email
)


# Test case registry
TEST_CASES = [
    {
        "name": "test_health_check",
        "function": test_health_check,
        "description": "Health check",
        "requires_session": False
    },
    {
        "name": "test_start_game",
        "function": test_start_game,
        "description": "Start game",
        "requires_session": False,
        "creates_session": True
    },
    {
        "name": "test_process_action_step",
        "function": test_process_action_step,
        "description": "Process action step",
        "requires_session": True
    },
    {
        "name": "test_context_changes_over_steps",
        "function": test_context_changes_over_steps,
        "description": "Context changes over steps",
        "requires_session": True
    },
    {
        "name": "test_multiple_steps_sequential",
        "function": test_multiple_steps_sequential,
        "description": "Multiple steps sequential",
        "requires_session": True
    },
    {
        "name": "test_get_current_context",
        "function": test_get_current_context,
        "description": "Get current context",
        "requires_session": True
    },
    {
        "name": "test_get_step_history",
        "function": test_get_step_history,
        "description": "Get step history",
        "requires_session": True
    },
    {
        "name": "test_session_isolation",
        "function": test_session_isolation,
        "description": "Session isolation",
        "requires_session": False
    },
    {
        "name": "test_invalid_session",
        "function": test_invalid_session,
        "description": "Invalid session",
        "requires_session": False
    },
    {
        "name": "test_missing_input",
        "function": test_missing_input,
        "description": "Missing input",
        "requires_session": True
    },
    {
        "name": "test_game_init_i18n",
        "function": test_game_init_i18n,
        "description": "i18n game initialization",
        "requires_session": False
    },
    {
        "name": "test_anonymous_to_registered",
        "function": test_anonymous_to_registered,
        "description": "Anonymous to registered",
        "requires_session": False
    },
    {
        "name": "test_user_login",
        "function": test_user_login,
        "description": "User login",
        "requires_session": False
    },
    {
        "name": "test_logout",
        "function": test_logout,
        "description": "Logout",
        "requires_session": False
    },
    {
        "name": "test_token_refresh",
        "function": test_token_refresh,
        "description": "Token refresh",
        "requires_session": False
    },
    {
        "name": "test_cross_user_session_access",
        "function": test_cross_user_session_access,
        "description": "Cross-user session access",
        "requires_session": False
    },
    {
        "name": "test_anonymous_session_isolation",
        "function": test_anonymous_session_isolation,
        "description": "Anonymous session isolation",
        "requires_session": False
    },
    {
        "name": "test_register_preserves_ownership",
        "function": test_register_preserves_ownership,
        "description": "Register preserves ownership",
        "requires_session": False
    },
    {
        "name": "test_invalid_credentials",
        "function": test_invalid_credentials,
        "description": "Invalid credentials",
        "requires_session": False
    },
    {
        "name": "test_duplicate_email",
        "function": test_duplicate_email,
        "description": "Duplicate email",
        "requires_session": False
    },
    {
        "name": "test_empty_password",
        "function": test_empty_password,
        "description": "Empty password",
        "requires_session": False
    },
    {
        "name": "test_malformed_email",
        "function": test_malformed_email,
        "description": "Malformed email",
        "requires_session": False
    },
    {
        "name": "test_rollback_to_step",
        "function": test_rollback_to_step,
        "description": "Rollback to step",
        "requires_session": False
    },
    {
        "name": "test_rollback_invalid_index",
        "function": test_rollback_invalid_index,
        "description": "Rollback invalid index",
        "requires_session": False
    }
]


def run_all_tests(service_url: str = None) -> bool:
    """Run all test suites

    Args:
        service_url: Backend service URL (defaults to Config.SERVICE_URL)

    Returns:
        True if all tests passed, False otherwise
    """
    # Use provided URL or fall back to config
    if service_url:
        Config.SERVICE_URL = service_url

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False

    # Display configuration
    Config.display()

    result = TestResult()
    session_id = None

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
        with BackendGameClient(service_url=Config.SERVICE_URL) as client:
            print(f"Connected to service: {Config.SERVICE_URL}")
            print(f"Service name: {client.service_name}")

            # Run selected test cases
            for case in cases_to_run:
                # Skip tests that require a session if we don't have one
                if case.get("requires_session") and not session_id:
                    continue

                try:
                    if case["name"] == "test_start_game":
                        session_id = case["function"](client, result)
                    elif case.get("requires_session"):
                        case["function"](client, result, session_id)
                    else:
                        case["function"](client, result)
                except Exception as e:
                    print(f"\n{case['description']} test failed: {e}")

    except ConnectionError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTip: Ensure WordVoyage Backend service is running")
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
        description="WordVoyage Backend End-to-End Tests"
    )
    parser.add_argument(
        "--url",
        default=None,
        help=f"Backend service URL (default: {Config.SERVICE_URL})"
    )

    args = parser.parse_args()

    success = run_all_tests(service_url=args.url)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
