#!/usr/bin/env python3
"""
Main test runner for OpenAI LLM end-to-end tests

Runs all test suites and reports results.
"""

import sys
import argparse
import logging
from .config import Config
from .test_client import LLMTestClient
from .test_scenarios import LLMTestScenarios

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_all_tests(service_url: str = None) -> bool:
    """Run all test suites

    Args:
        service_url: OpenAI LLM service URL (defaults to Config.SERVICE_URL)

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

    try:
        with LLMTestClient(Config.SERVICE_URL) as client:
            print(f"🔗 Connected to service: {Config.SERVICE_URL}")

            # Get service health info
            health = client.health_check()
            print(f"📋 Service info: {health}")

            # Run test scenarios
            scenarios = LLMTestScenarios(client)
            return scenarios.run_all_tests()

    except ConnectionError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\n💡 Tip: Ensure OpenAI LLM service is running and accessible")
        return False

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="OpenAI LLM End-to-End Tests"
    )
    parser.add_argument(
        "--url",
        default=None,
        help=f"OpenAI LLM service URL (default: {Config.SERVICE_URL})"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    success = run_all_tests(service_url=args.url)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())