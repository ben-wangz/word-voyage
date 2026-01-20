"""Session and history tests"""

import time
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def test_get_current_context(client: BackendGameClient, result: TestResult):
    """Test GET /api/game/context/:sessionId endpoint"""
    test_name = "Get Current Context"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        session_id = client.get_session_id()
        print(f"\nGetting context for session: {session_id}")

        response = client.get_context()

        print(f"\nContext response:")

        # Validate response
        assert 'context' in response, "Expected context in response"

        context = response.get('context', {})
        assert 'state' in context, "Expected state in context"

        state = context.get('state', {})

        print(f"  Context fields: {len(state)}")
        for key in state:
            field_data = state[key]
            print(f"    - {key}: {field_data.get('value')} (type: {field_data.get('type')})")

        print("  ✓ Current context retrieved successfully")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_get_step_history(client: BackendGameClient, result: TestResult):
    """Test GET /api/game/history/:sessionId endpoint"""
    test_name = "Get Step History"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        session_id = client.get_session_id()
        print(f"\nGetting history for session: {session_id}")

        response = client.get_history()

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

        # Create second client for isolated session
        client2 = BackendGameClient(client.service_url, client.timeout)

        # Start first game
        game1 = client.start_game()
        session1_id = game1.get('sessionId')
        print(f"  Session 1: {session1_id}")

        # Start second game
        game2 = client2.start_game()
        session2_id = game2.get('sessionId')
        print(f"  Session 2: {session2_id}")

        # Verify they're different
        assert session1_id != session2_id, "Expected different session IDs"

        # Process different steps in each session
        print("\nProcessing steps in different sessions...")

        response1 = client.process_step("Action in session 1")
        step1 = response1.get('step')

        response2 = client2.process_step("Action in session 2")
        step2 = response2.get('step')

        # Get histories
        history1 = client.get_history()
        history2 = client2.get_history()

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

        client2.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_rollback_to_step(client: BackendGameClient, result: TestResult):
    """Test POST /api/game/rollback endpoint"""
    test_name = "Rollback to Step"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        # Create fresh client for isolated test
        test_client = client.fresh_copy()
        test_client.start_game()
        print("\nGame started")

        # Process 3 steps
        for i in range(3):
            test_client.process_step(f"Action {i+1}")
        print("Processed 3 steps")

        # Get history before rollback
        history_before = test_client.get_history()
        steps_before = history_before.get('steps', [])
        print(f"History before rollback: {len(steps_before)} steps")
        assert len(steps_before) == 4, f"Expected 4 steps (1 initial + 3 actions), got {len(steps_before)}"

        # Rollback to step 1 (0-based index)
        print("\nRolling back to step 1...")
        rollback_response = test_client.rollback(1)

        assert 'step' in rollback_response, "Expected step in rollback response"
        assert 'sessionId' in rollback_response, "Expected sessionId in rollback response"

        # Get history after rollback
        history_after = test_client.get_history()
        steps_after = history_after.get('steps', [])
        print(f"History after rollback: {len(steps_after)} steps")

        # Verify history length
        assert len(steps_after) == 2, f"Expected 2 steps after rollback to index 1, got {len(steps_after)}"

        # Verify current step is the one we rolled back to
        current_step = rollback_response.get('step')
        assert current_step.get('id') == steps_after[1].get('id'), "Current step should match step at index 1"

        print("  ✓ Rollback successful")

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_rollback_invalid_index(client: BackendGameClient, result: TestResult):
    """Test rollback with invalid step index"""
    test_name = "Rollback Invalid Index"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        # Create fresh client for isolated test
        test_client = client.fresh_copy()
        test_client.start_game()
        test_client.process_step("Action 1")
        print("\nGame started with 2 steps")

        # Test negative index
        print("\nTesting negative index...")
        response = test_client.rollback_no_raise(-1)
        assert response.status_code == 400, f"Expected 400 for negative index, got {response.status_code}"
        print("  ✓ Negative index rejected")

        # Test out of range index
        print("\nTesting out of range index...")
        response = test_client.rollback_no_raise(999)
        assert response.status_code == 400, f"Expected 400 for out of range index, got {response.status_code}"
        print("  ✓ Out of range index rejected")

        # Test invalid type
        print("\nTesting invalid type...")
        response = test_client.rollback_no_raise("invalid")
        assert response.status_code == 400, f"Expected 400 for invalid type, got {response.status_code}"
        print("  ✓ Invalid type rejected")

        test_client.close()
        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
