"""Test scenarios for OpenAI LLM Service"""

import json
import logging
from typing import Dict, Any, List
from .test_client import LLMTestClient
from .test_data import (
    SAMPLE_CONTEXT, EVENT_SCHEMA, PRE_LOG_SUMMARY,
    TEST_PROMPTS, USER_INPUTS, SCHEMA_VALIDATION_TESTS
)

logger = logging.getLogger(__name__)


class LLMTestScenarios:
    """Test scenarios for OpenAI LLM Service"""

    def __init__(self, client: LLMTestClient):
        self.client = client

    def run_health_check(self) -> bool:
        """Test service health check"""
        try:
            print("Testing health check...")
            health = self.client.health_check()

            required_fields = ["status", "model", "service"]
            for field in required_fields:
                if field not in health:
                    print(f"❌ Health check missing required field: {field}")
                    return False

            if health["status"] != "healthy":
                print(f"❌ Service not healthy: {health}")
                return False

            print(f"✅ Health check passed - Service: {health['service']}, Model: {health['model']}")
            return True

        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def test_basic_structured_generation(self) -> bool:
        """Test basic structured generation"""
        try:
            print("\nTesting basic structured generation...")

            result = self.client.generate_structured(
                prompt="Generate a game event based on the current situation",
                context=SAMPLE_CONTEXT,
                schema=EVENT_SCHEMA
            )

            if not result.get("success"):
                print(f"❌ Structured generation failed: {result.get('message')}")
                return False

            if "result" not in result:
                print("❌ Response missing result field")
                return False

            result_data = result["result"]
            if "event_description" not in result_data or "context_changes" not in result_data:
                print("❌ Result missing required fields")
                return False

            print(f"✅ Basic structured generation passed")
            print(f"   Event: {result_data['event_description'][:100]}...")
            return True

        except Exception as e:
            print(f"❌ Basic structured generation failed: {e}")
            return False

    def test_with_user_input(self) -> bool:
        """Test structured generation with user input"""
        try:
            print("\nTesting structured generation with user input...")

            result = self.client.generate_structured(
                prompt="Generate a game event based on the user's action",
                context=SAMPLE_CONTEXT,
                schema=EVENT_SCHEMA,
                pre_log_summary=PRE_LOG_SUMMARY,
                user_input="I decide to explore the nearby forest"
            )

            if not result.get("success"):
                print(f"❌ Generation with user input failed: {result.get('message')}")
                return False

            result_data = result["result"]
            if not result_data.get("event_description"):
                print("❌ No event description generated")
                return False

            print(f"✅ Generation with user input passed")
            print(f"   Event: {result_data['event_description'][:100]}...")
            return True

        except Exception as e:
            print(f"❌ Generation with user input failed: {e}")
            return False

    def test_context_validation(self) -> bool:
        """Test context size validation"""
        try:
            print("\nTesting context validation...")

            for test_case in SCHEMA_VALIDATION_TESTS:
                print(f"  Testing: {test_case['description']}")

                context = test_case.get("context_override", SAMPLE_CONTEXT)

                result = self.client.generate_structured(
                    prompt="Test validation",
                    context=context,
                    schema=EVENT_SCHEMA
                )

                expected_success = test_case.get("expected_success", True)
                actual_success = result.get("success", False)

                if expected_success != actual_success:
                    print(f"❌ Test '{test_case['name']}' failed - Expected success: {expected_success}, Got: {actual_success}")
                    if not actual_success:
                        print(f"   Error: {result.get('message')}")
                    return False

                if not expected_success and "expected_error_code" in test_case:
                    actual_error_code = result.get("error_code")
                    expected_error_code = test_case["expected_error_code"]
                    if actual_error_code != expected_error_code:
                        print(f"❌ Test '{test_case['name']}' failed - Expected error: {expected_error_code}, Got: {actual_error_code}")
                        return False

                print(f"    ✅ Passed")

            print(f"✅ Context validation tests passed")
            return True

        except Exception as e:
            print(f"❌ Context validation tests failed: {e}")
            return False

    def test_streaming(self) -> bool:
        """Test streaming generation"""
        try:
            print("\nTesting streaming generation...")

            request_data = {
                "prompt": "Generate a detailed game event",
                "context": SAMPLE_CONTEXT,
                "schema": EVENT_SCHEMA,
                "stream": True,
                "user_input": "I carefully examine the alien vegetation"
            }

            chunks = self.client.generate_structured_stream(request_data)

            if not chunks:
                print("❌ No chunks received from streaming")
                return False

            print(f"✅ Streaming generation passed - Received {len(chunks)} chunks")
            return True

        except Exception as e:
            print(f"❌ Streaming generation failed: {e}")
            return False

    def test_multiple_requests(self) -> bool:
        """Test handling multiple requests"""
        try:
            print("\nTesting multiple requests...")

            results = []
            for i, (prompt, user_input) in enumerate(zip(TEST_PROMPTS[:2], USER_INPUTS[:2])):
                print(f"  Request {i+1}: {prompt[:30]}...")

                result = self.client.generate_structured(
                    prompt=prompt,
                    context=SAMPLE_CONTEXT,
                    schema=EVENT_SCHEMA,
                    user_input=user_input
                )

                if not result.get("success"):
                    print(f"❌ Request {i+1} failed: {result.get('message')}")
                    return False

                results.append(result["result"])

            print(f"✅ Multiple requests test passed - Generated {len(results)} responses")
            return True

        except Exception as e:
            print(f"❌ Multiple requests test failed: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all test scenarios"""
        print("🚀 Starting OpenAI LLM Service End-to-End Tests")
        print("=" * 50)

        tests = [
            ("Health Check", self.run_health_check),
            ("Basic Structured Generation", self.test_basic_structured_generation),
            ("Generation with User Input", self.test_with_user_input),
            ("Context Validation", self.test_context_validation),
            ("Multiple Requests", self.test_multiple_requests),
            ("Streaming Generation", self.test_streaming),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("💥 Some tests failed!")
            return False