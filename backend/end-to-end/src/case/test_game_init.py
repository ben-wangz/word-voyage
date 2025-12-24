"""Game initialization tests"""

import time
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def test_start_game(client: BackendGameClient, result: TestResult):
    """Test POST /api/game/start endpoint"""
    test_name = "Start Game"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        response = client.start_game()

        print(f"\nStart game response:")
        print(f"  Session ID: {response.get('sessionId')}")
        print(f"  Step ID: {response.get('step', {}).get('id')}")

        # Validate response structure
        assert 'sessionId' in response, \
            "Expected sessionId in response"
        assert 'step' in response, \
            "Expected step in response"

        session_id = response.get('sessionId')
        step = response.get('step')

        # Validate step structure
        assert 'id' in step, "Expected id in step"
        assert 'timestamp' in step, "Expected timestamp in step"
        assert 'userInput' in step, "Expected userInput in step"
        assert 'inputType' in step, "Expected inputType in step"
        assert 'context' in step, "Expected context in step"
        assert 'event' in step, "Expected event in step"
        assert 'preLogSummary' in step, "Expected preLogSummary in step"

        # Validate initial context
        context = step.get('context', {})
        assert 'state' in context, "Expected state in context"
        assert 'gameTime' in context, "Expected gameTime in context"

        state = context.get('state', {})
        required_fields = ['health', 'hunger', 'thirst', 'energy', 'location']
        for field in required_fields:
            assert field in state, f"Expected {field} in initial context"
            field_data = state[field]
            assert 'value' in field_data, f"Expected value in {field}"
            assert 'type' in field_data, f"Expected type in {field}"

        print(f"\n  Initial context fields: {list(state.keys())}")
        print(f"  Game time: {context.get('gameTime')}")

        # Validate event
        event = step.get('event', {})
        assert 'description' in event, "Expected description in event"
        assert 'contextChanges' in event, "Expected contextChanges in event"
        assert len(event.get('description', '')) > 0, "Expected non-empty event description"

        print(f"  Event description: {event.get('description')[:80]}...")

        # Validate preLogSummary
        pre_log = step.get('preLogSummary', {})
        assert 'summary' in pre_log, "Expected summary in preLogSummary"
        assert 'recentEvents' in pre_log, "Expected recentEvents in preLogSummary"
        assert 'generatedAt' in pre_log, "Expected generatedAt in preLogSummary"

        print("  ✓ Game started successfully with correct initial state")

        result.add(test_name, "success", time.time() - start_time)
        return session_id

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
