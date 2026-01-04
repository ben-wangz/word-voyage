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


# Test case registry
TEST_CASES = [
    {
        "name": "test_health_check",
        "function": test_health_check,
        "description": "Health check"
    },
    {
        "name": "test_simple_generation",
        "function": test_simple_generation,
        "description": "Simple generation"
    },
    {
        "name": "test_context_changes",
        "function": test_context_changes,
        "description": "Context changes"
    },
    {
        "name": "test_context_limit",
        "function": test_context_limit,
        "description": "Context limit"
    }
]


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
        with LLMClient(service_url=Config.SERVICE_URL) as client:
            print(f"Connected to service: {Config.SERVICE_URL}")
            print(f"Service status: {client.service_name}")
            print()

            # Run selected test cases
            for case in cases_to_run:
                try:
                    case["function"](client, result)
                except Exception as e:
                    print(f"\n{case['description']} test failed: {e}")

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
