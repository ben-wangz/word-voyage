"""Test data for OpenAI LLM Service tests"""

# Sample context for game event generation
SAMPLE_CONTEXT = {
    "health": {
        "value": 85,
        "type": "number",
        "description": "Current health points"
    },
    "hunger": {
        "value": 30,
        "type": "number",
        "description": "Hunger level (lower is better)"
    },
    "thirst": {
        "value": 45,
        "type": "number",
        "description": "Thirst level (lower is better)"
    },
    "location": {
        "value": "spaceship_crash_site",
        "type": "string",
        "description": "Current location"
    },
    "energy": {
        "value": 70,
        "type": "number",
        "description": "Energy level"
    }
}

# Sample schema for event generation
EVENT_SCHEMA = {
    "event_description": {
        "type": "string",
        "description": "A descriptive text of what happens in the game world during this time period"
    },
    "context_changes": {
        "type": "object",
        "description": "Changes to the game context, with field names as keys and new values as values. Use null to delete a field."
    }
}

# Sample pre-log summary
PRE_LOG_SUMMARY = {
    "summary": "You just crashed your spaceship on an unknown planet and are assessing your situation.",
    "recent_events": [
        "You wake up amidst the wreckage of your spaceship.",
        "The emergency systems are still beeping, warning of low oxygen levels.",
        "You check your survival kit and find basic supplies."
    ]
}

# Test prompts
TEST_PROMPTS = [
    "Generate a game event based on the current situation",
    "Create an interesting event that moves the story forward",
    "Generate a survival challenge that the player must face"
]

# Sample user inputs
USER_INPUTS = [
    "I decide to explore the nearby forest",
    "I check my spaceship's emergency supplies",
    "I try to repair the communication system"
]

# Validation test cases
SCHEMA_VALIDATION_TESTS = [
    {
        "name": "valid_response",
        "description": "Should return valid JSON matching schema",
        "expected_success": True
    },
    {
        "name": "large_context",
        "description": "Should handle context at maximum size",
        "expected_success": True,
        "context_override": {f"field_{i}": {"value": i, "type": "number", "description": f"Test field {i}"} for i in range(16)}
    },
    {
        "name": "oversized_context",
        "description": "Should reject context exceeding maximum",
        "expected_success": False,
        "context_override": {f"field_{i}": {"value": i, "type": "number", "description": f"Test field {i}"} for i in range(20)},
        "expected_error_code": "CONTEXT_TOO_LARGE"
    }
]