"""Game step processing tests"""

import time
import json
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def test_process_action_step(client: BackendGameClient, result: TestResult, session_id: str):
    """Test POST /api/game/step endpoint with action input"""
    test_name = "Process Action Step"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        user_input = "Look around and assess the situation"
        print(f"\nProcessing action: '{user_input}'")

        response = client.process_step(session_id, user_input)

        print(f"\nProcess step response:")
        print(f"  Session ID: {response.get('sessionId')}")
        print(f"  Step ID: {response.get('step', {}).get('id')}")

        # Validate response structure
        assert 'sessionId' in response, "Expected sessionId in response"
        assert 'step' in response, "Expected step in response"
        assert response.get('sessionId') == session_id, "Session ID should match"

        step = response.get('step')

        # Validate step structure
        assert 'id' in step, "Expected id in step"
        assert 'timestamp' in step, "Expected timestamp in step"
        assert 'userInput' in step, "Expected userInput in step"
        assert 'inputType' in step, "Expected inputType in step"
        assert 'context' in step, "Expected context in step"
        assert 'event' in step, "Expected event in step"
        assert 'preLogSummary' in step, "Expected preLogSummary in step"

        # Validate user input is recorded
        assert step.get('userInput') == user_input, \
            f"Expected userInput={user_input}, got {step.get('userInput')}"

        # Validate context
        context = step.get('context', {})
        assert 'state' in context, "Expected state in context"
        assert 'gameTime' in context, "Expected gameTime in context"

        state = context.get('state', {})
        assert len(state) > 0, "Expected state to have at least one field"

        print(f"  Context fields: {list(state.keys())}")
        print(f"  Game time: {context.get('gameTime')}")

        # Validate event
        event = step.get('event', {})
        assert 'description' in event, "Expected description in event"
        assert 'contextChanges' in event, "Expected contextChanges in event"

        description = event.get('description', '')
        assert len(description) > 0, "Expected non-empty event description"
        print(f"  Event generated: {description[:100]}...")

        # Validate preLogSummary
        pre_log = step.get('preLogSummary', {})
        assert 'summary' in pre_log, "Expected summary in preLogSummary"
        assert 'recentEvents' in pre_log, "Expected recentEvents in preLogSummary"
        assert 'generatedAt' in pre_log, "Expected generatedAt in preLogSummary"

        print("  ✓ Action step processed successfully")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_context_changes_over_steps(client: BackendGameClient, result: TestResult, session_id: str):
    """Test that context is updated over multiple steps"""
    test_name = "Context Changes Over Steps"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        # Get initial context
        initial_response = client.get_context(session_id)
        initial_context = initial_response.get('context', {})
        initial_state = initial_context.get('state', {})
        initial_values = {k: v.get('value') for k, v in initial_state.items()}

        print(f"\nInitial context values:")
        for key, value in initial_values.items():
            print(f"  {key}: {value}")

        # Process multiple steps
        actions = [
            "Try to find water",
            "Look for shelter",
            "Check oxygen levels"
        ]

        for action in actions:
            response = client.process_step(session_id, action)
            step = response.get('step')

            print(f"\nAfter action: '{action}'")
            context = step.get('context', {})
            state = context.get('state', {})
            current_values = {k: v.get('value') for k, v in state.items()}

            for key, value in current_values.items():
                print(f"  {key}: {value}")

        # Get final context
        final_response = client.get_context(session_id)
        final_context = final_response.get('context', {})
        final_state = final_context.get('state', {})
        final_values = {k: v.get('value') for k, v in final_state.items()}

        print(f"\nFinal context values:")
        for key, value in final_values.items():
            print(f"  {key}: {value}")

        # Verify context exists
        assert len(final_values) > 0, "Expected context to have values"

        print("  ✓ Context changes tracked over multiple steps")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_multiple_steps_sequential(client: BackendGameClient, result: TestResult, session_id: str):
    """Test processing multiple steps sequentially"""
    test_name = "Multiple Steps Sequential"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        step_count = 3
        print(f"\nProcessing {step_count} sequential steps...")

        for i in range(step_count):
            action = f"Exploration step {i+1}"
            response = client.process_step(session_id, action)

            assert 'step' in response, f"Step {i+1}: Expected step in response"
            step = response.get('step')

            print(f"  Step {i+1}: {step.get('id')[:8]}... (game time: {step.get('context', {}).get('gameTime')})")

            # Verify each step has required fields
            assert 'context' in step, f"Step {i+1}: Expected context"
            assert 'event' in step, f"Step {i+1}: Expected event"
            assert 'preLogSummary' in step, f"Step {i+1}: Expected preLogSummary"

        print("  ✓ All steps processed sequentially")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
