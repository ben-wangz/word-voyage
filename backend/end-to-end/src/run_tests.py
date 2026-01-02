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
    test_session_isolation
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

    try:
        with BackendGameClient(service_url=Config.SERVICE_URL) as client:
            print(f"Connected to service: {Config.SERVICE_URL}")
            print(f"Service name: {client.service_name}")

            # Test 1: Health check
            try:
                test_health_check(client, result)
            except Exception as e:
                print(f"\nHealth check failed: {e}")

            # Test 2: Start game
            try:
                session_id = test_start_game(client, result)
            except Exception as e:
                print(f"\nStart game test failed: {e}")

            # Test 3: Process action step
            if session_id:
                try:
                    test_process_action_step(client, result, session_id)
                except Exception as e:
                    print(f"\nProcess action step test failed: {e}")

            # Test 4: Context changes over steps
            if session_id:
                try:
                    test_context_changes_over_steps(client, result, session_id)
                except Exception as e:
                    print(f"\nContext changes test failed: {e}")

            # Test 5: Multiple steps sequential
            if session_id:
                try:
                    test_multiple_steps_sequential(client, result, session_id)
                except Exception as e:
                    print(f"\nMultiple steps test failed: {e}")

            # Test 6: Get current context
            if session_id:
                try:
                    test_get_current_context(client, result, session_id)
                except Exception as e:
                    print(f"\nGet context test failed: {e}")

            # Test 7: Get step history
            if session_id:
                try:
                    test_get_step_history(client, result, session_id)
                except Exception as e:
                    print(f"\nGet history test failed: {e}")

            # Test 8: Session isolation
            try:
                test_session_isolation(client, result)
            except Exception as e:
                print(f"\nSession isolation test failed: {e}")

            # Test 9: Invalid session ID
            try:
                test_invalid_session(client, result)
            except Exception as e:
                print(f"\nInvalid session test failed: {e}")

            # Test 10: Missing input
            if session_id:
                try:
                    test_missing_input(client, result, session_id)
                except Exception as e:
                    print(f"\nMissing input test failed: {e}")

            # Test 11: i18n Game Initialization
            try:
                test_game_init_i18n(client, result)
            except Exception as e:
                print(f"\ni18n game initialization test failed: {e}")

            # Test 12-22: Authentication tests
            try:
                test_anonymous_to_registered(client, result)
            except Exception as e:
                print(f"\nAnonymous to registered test failed: {e}")

            try:
                test_user_login(client, result)
            except Exception as e:
                print(f"\nUser login test failed: {e}")

            try:
                test_logout(client, result)
            except Exception as e:
                print(f"\nLogout test failed: {e}")

            try:
                test_token_refresh(client, result)
            except Exception as e:
                print(f"\nToken refresh test failed: {e}")

            try:
                test_cross_user_session_access(client, result)
            except Exception as e:
                print(f"\nCross-user session access test failed: {e}")

            try:
                test_anonymous_session_isolation(client, result)
            except Exception as e:
                print(f"\nAnonymous session isolation test failed: {e}")

            try:
                test_register_preserves_ownership(client, result)
            except Exception as e:
                print(f"\nRegister preserves ownership test failed: {e}")

            try:
                test_invalid_credentials(client, result)
            except Exception as e:
                print(f"\nInvalid credentials test failed: {e}")

            try:
                test_duplicate_email(client, result)
            except Exception as e:
                print(f"\nDuplicate email test failed: {e}")

            try:
                test_empty_password(client, result)
            except Exception as e:
                print(f"\nEmpty password test failed: {e}")

            try:
                test_malformed_email(client, result)
            except Exception as e:
                print(f"\nMalformed email test failed: {e}")

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
