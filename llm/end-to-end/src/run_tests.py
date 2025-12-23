#!/usr/bin/env python3
"""
Main test runner for LLM Service end-to-end tests

Runs all test suites and reports results.
"""

import sys
import argparse
from .config import Config
from .utils.llm_client import LLMClient
from .utils.test_result import TestResult
from .case.test_health import test_health_check
from .case.test_generate import (
    test_simple_generation,
    test_context_changes,
    test_context_limit
)


def run_all_tests(service_url: str = None) -> bool:
    """Run all test suites

    Args:
        service_url: LLM service URL (defaults to Config.SERVICE_URL)

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

    try:
        with LLMClient(service_url=Config.SERVICE_URL) as client:
            print(f"Connected to service: {Config.SERVICE_URL}")
            print(f"Service status: {client.service_name}")
            print()

            # Run all tests
            try:
                test_health_check(client, result)
            except Exception as e:
                print(f"\nHealth check failed: {e}")

            try:
                test_simple_generation(client, result)
            except Exception as e:
                print(f"\nSimple generation test failed: {e}")

            try:
                test_context_changes(client, result)
            except Exception as e:
                print(f"\nContext changes test failed: {e}")

            try:
                test_context_limit(client, result)
            except Exception as e:
                print(f"\nContext limit test failed: {e}")

    except ConnectionError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTip: Ensure LLM service is running and OPENAI_API_KEY is set")
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
        description="LLM Service End-to-End Tests"
    )
    parser.add_argument(
        "--url",
        default=None,
        help=f"LLM service URL (default: {Config.SERVICE_URL})"
    )

    args = parser.parse_args()

    success = run_all_tests(service_url=args.url)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
