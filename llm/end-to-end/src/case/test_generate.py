"""Event generation tests"""

from ..utils.llm_client import LLMClient
from ..utils.test_result import TestResult


def test_simple_generation(client: LLMClient, result: TestResult):
    """Test simple event generation

    Args:
        client: LLM client
        result: Test result tracker
    """
    print("Testing simple event generation...")

    try:
        # Minimal context
        context = {
            "health": {
                "value": 100,
                "type": "number",
                "description": "Player health points"
            }
        }

        # Schema for event generation
        schema = {
            "event_description": {
                "type": "string",
                "description": "Narrative description of the event"
            },
            "context_changes": {
                "type": "object",
                "description": "Changes to context fields"
            }
        }

        # Simple prompt
        prompt = "You are a game master. Generate an event based on the player's action."
        user_input = "look around"

        response = client.generate_structured(
            prompt=prompt,
            context=context,
            schema=schema,
            user_input=user_input
        )

        # Verify response structure
        assert response["success"] is True, f"Generation failed: {response.get('message')}"
        assert "result" in response, "Missing 'result' in response"
        assert "event_description" in response["result"], "Missing 'event_description'"

        event_desc = response["result"]["event_description"]
        message = f"Generated event: {event_desc[:100]}..."
        result.add_result("simple_generation", "passed", message)
        print(f"✓ Simple generation passed")
        print(f"  Event: {event_desc}")

    except Exception as e:
        result.add_result("simple_generation", "failed", str(e), str(e))
        print(f"✗ Simple generation failed: {e}")
        raise


def test_context_changes(client: LLMClient, result: TestResult):
    """Test event generation with context changes

    Args:
        client: LLM client
        result: Test result tracker
    """
    print("Testing context changes...")

    try:
        # Initial context
        context = {
            "health": {
                "value": 100,
                "type": "number",
                "description": "Player health points"
            },
            "energy": {
                "value": 80,
                "type": "number",
                "description": "Player energy level"
            }
        }

        # Schema
        schema = {
            "event_description": {
                "type": "string",
                "description": "Narrative description of the event"
            },
            "context_changes": {
                "type": "object",
                "description": "Changes to context fields (only changed fields)"
            }
        }

        # Prompt that should trigger context changes
        prompt = "You are a game master. The player performs a strenuous action. Reduce their energy by 20 points."
        user_input = "climb a steep hill"

        response = client.generate_structured(
            prompt=prompt,
            context=context,
            schema=schema,
            user_input=user_input
        )

        # Verify response
        assert response["success"] is True, f"Generation failed: {response.get('message')}"
        assert "result" in response, "Missing 'result' in response"
        assert "context_changes" in response["result"], "Missing 'context_changes'"

        context_changes = response["result"]["context_changes"]
        message = f"Context changes: {list(context_changes.keys())}"
        result.add_result("context_changes", "passed", message)
        print(f"✓ Context changes test passed")
        print(f"  Changes: {context_changes}")

    except Exception as e:
        result.add_result("context_changes", "failed", str(e), str(e))
        print(f"✗ Context changes test failed: {e}")
        raise


def test_context_limit(client: LLMClient, result: TestResult):
    """Test context field limit enforcement

    Args:
        client: LLM client
        result: Test result tracker
    """
    print("Testing context field limit...")

    try:
        # Create context with too many fields (> 16)
        context = {}
        for i in range(20):
            context[f"field_{i}"] = {
                "value": i,
                "type": "number",
                "description": f"Test field {i}"
            }

        schema = {
            "event_description": {
                "type": "string",
                "description": "Event description"
            },
            "context_changes": {
                "type": "object",
                "description": "Context changes"
            }
        }

        response = client.generate_structured(
            prompt="Generate a test event",
            context=context,
            schema=schema,
            user_input="test"
        )

        # Should return error
        assert response["success"] is False, "Should fail with too many context fields"
        assert response["error_code"] == "CONTEXT_TOO_LARGE", f"Wrong error code: {response.get('error_code')}"

        message = "Context limit correctly enforced"
        result.add_result("context_limit", "passed", message)
        print(f"✓ Context limit test passed")

    except AssertionError as e:
        result.add_result("context_limit", "failed", str(e), str(e))
        print(f"✗ Context limit test failed: {e}")
        raise
    except Exception as e:
        # Unexpected error
        result.add_result("context_limit", "failed", str(e), str(e))
        print(f"✗ Context limit test failed with unexpected error: {e}")
        raise
