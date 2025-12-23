"""Health check tests"""

from ..utils.llm_client import LLMClient
from ..utils.test_result import TestResult


def test_health_check(client: LLMClient, result: TestResult):
    """Test service health check endpoint

    Args:
        client: LLM client
        result: Test result tracker
    """
    print("Testing health check endpoint...")

    try:
        health = client.health_check()

        # Verify response structure
        assert "status" in health, "Missing 'status' in health response"
        assert health["status"] == "healthy", "Service status is not healthy"

        assert "service" in health, "Missing 'service' in health response"
        assert health["service"] == "openai-llm", f"Unexpected service: {health['service']}"

        assert "model" in health, "Missing 'model' in health response"
        assert "context_max_fields" in health, "Missing 'context_max_fields' in health response"

        message = f"Service is healthy (model: {health['model']}, max fields: {health['context_max_fields']})"
        result.add_result("health_check", "passed", message)
        print(f"✓ Health check passed: {message}")

    except Exception as e:
        result.add_result("health_check", "failed", str(e), str(e))
        print(f"✗ Health check failed: {e}")
        raise
