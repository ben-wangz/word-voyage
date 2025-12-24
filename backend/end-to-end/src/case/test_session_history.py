"""Session and history tests"""

import time
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def test_get_current_context(client: BackendGameClient, result: TestResult, session_id: str):
    """Test GET /api/game/context/:sessionId endpoint"""
    test_name = "Get Current Context"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        print(f"\nGetting context for session: {session_id}")

        response = client.get_context(session_id)

        print(f"\nContext response:")

        # Validate response
        assert 'context' in response, "Expected context in response"

        context = response.get('context', {})
        assert 'state' in context, "Expected state in context"
        assert 'gameTime' in context, "Expected gameTime in context"

        state = context.get('state', {})
        game_time = context.get('gameTime')

        print(f"  Game time: {game_time}")
        print(f"  Context fields: {len(state)}")
        for key in state:
            field_data = state[key]
            print(f"    - {key}: {field_data.get('value')} (type: {field_data.get('type')})")

        print("  ✓ Current context retrieved successfully")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_get_step_history(client: BackendGameClient, result: TestResult, session_id: str):
    """Test GET /api/game/history/:sessionId endpoint"""
    test_name = "Get Step History"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        print(f"\nGetting history for session: {session_id}")

        response = client.get_history(session_id)

        print(f"\nHistory response:")

        # Validate response
        assert 'steps' in response, "Expected steps in response"

        steps = response.get('steps', [])
        print(f"  Total steps: {len(steps)}")

        # Validate steps structure
        assert isinstance(steps, list), "Expected steps to be a list"
        assert len(steps) > 0, "Expected at least one step in history"

        # Validate each step
        for idx, step in enumerate(steps):
            assert 'id' in step, f"Step {idx}: Expected id"
            assert 'timestamp' in step, f"Step {idx}: Expected timestamp"
            assert 'userInput' in step, f"Step {idx}: Expected userInput"
            assert 'inputType' in step, f"Step {idx}: Expected inputType"
            assert 'context' in step, f"Step {idx}: Expected context"
            assert 'event' in step, f"Step {idx}: Expected event"
            assert 'preLogSummary' in step, f"Step {idx}: Expected preLogSummary"

            if idx < 3:  # Print first 3 steps
                print(f"\n  Step {idx+1}:")
                print(f"    ID: {step.get('id')[:8]}...")
                print(f"    Input: {step.get('userInput')}")
                print(f"    Game Time: {step.get('context', {}).get('gameTime')}")
                print(f"    Event: {step.get('event', {}).get('description', '')[:60]}...")

        print(f"\n  ✓ Step history retrieved successfully ({len(steps)} steps)")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_session_isolation(client: BackendGameClient, result: TestResult):
    """Test that multiple sessions are isolated from each other"""
    test_name = "Session Isolation"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        print("\nCreating two separate game sessions...")

        # Start first game
        game1 = client.start_game()
        session1_id = game1.get('sessionId')
        print(f"  Session 1: {session1_id}")

        # Start second game
        game2 = client.start_game()
        session2_id = game2.get('sessionId')
        print(f"  Session 2: {session2_id}")

        # Verify they're different
        assert session1_id != session2_id, "Expected different session IDs"

        # Process different steps in each session
        print("\nProcessing steps in different sessions...")

        response1 = client.process_step(session1_id, "Action in session 1")
        step1 = response1.get('step')

        response2 = client.process_step(session2_id, "Action in session 2")
        step2 = response2.get('step')

        # Get histories
        history1 = client.get_history(session1_id)
        history2 = client.get_history(session2_id)

        steps1 = history1.get('steps', [])
        steps2 = history2.get('steps', [])

        print(f"\n  Session 1 history: {len(steps1)} steps")
        print(f"  Session 2 history: {len(steps2)} steps")

        # Verify histories are different
        assert len(steps1) > 0, "Expected steps in session 1"
        assert len(steps2) > 0, "Expected steps in session 2"

        # Collect step IDs from each session
        step_ids_1 = {s.get('id') for s in steps1}
        step_ids_2 = {s.get('id') for s in steps2}

        # Verify no overlap
        overlap = step_ids_1 & step_ids_2
        assert len(overlap) == 0, f"Expected no step overlap between sessions, found {len(overlap)}"

        print("  ✓ Sessions are properly isolated")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
