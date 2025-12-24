"""Error handling tests"""

import time
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def test_invalid_session(client: BackendGameClient, result: TestResult):
    """Test that invalid session ID returns 404"""
    test_name = "Invalid Session ID"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        invalid_session_id = "00000000-0000-0000-0000-000000000000"
        print(f"\nTrying to process step with invalid session: {invalid_session_id}")

        try:
            response = client.process_step(invalid_session_id, "Test action")
            # Should not reach here
            raise AssertionError("Expected request to fail with 404, but it succeeded")
        except Exception as e:
            error_str = str(e)
            if "404" in error_str or "not found" in error_str.lower():
                print(f"  ✓ Correctly returned 404 for invalid session")
            else:
                raise AssertionError(f"Expected 404 error, got: {error_str}")

        # Also test get_context with invalid session
        print(f"\nTrying to get context with invalid session: {invalid_session_id}")

        try:
            response = client.get_context(invalid_session_id)
            # Should not reach here
            raise AssertionError("Expected request to fail with 404, but it succeeded")
        except Exception as e:
            error_str = str(e)
            if "404" in error_str or "not found" in error_str.lower():
                print(f"  ✓ Correctly returned 404 for invalid session")
            else:
                raise AssertionError(f"Expected 404 error, got: {error_str}")

        result.add(test_name, "success", time.time() - start_time)

    except AssertionError as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_missing_input(client: BackendGameClient, result: TestResult, session_id: str):
    """Test that missing input returns 400"""
    test_name = "Missing Input"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        print("\nTrying to process step without input...")

        # Send request with empty input
        try:
            response = client.process_step_raw({"sessionId": session_id, "input": ""})
            if response.status_code == 400:
                print(f"  ✓ Correctly returned 400 for empty input")
            else:
                raise AssertionError(f"Expected 400 for empty input, got {response.status_code}")
        except AssertionError:
            raise
        except Exception as e:
            # httpx might raise an exception for 400
            error_str = str(e)
            if "400" in error_str:
                print(f"  ✓ Correctly returned 400 for empty input")
            else:
                raise AssertionError(f"Expected 400 error, got: {error_str}")

        # Send request without input field
        print("\nTrying to process step without input field...")
        try:
            response = client.process_step_raw({"sessionId": session_id})
            if response.status_code == 400:
                print(f"  ✓ Correctly returned 400 for missing input field")
            else:
                raise AssertionError(f"Expected 400 for missing input, got {response.status_code}")
        except AssertionError:
            raise
        except Exception as e:
            error_str = str(e)
            if "400" in error_str:
                print(f"  ✓ Correctly returned 400 for missing input field")
            else:
                raise AssertionError(f"Expected 400 error, got: {error_str}")

        result.add(test_name, "success", time.time() - start_time)

    except AssertionError as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_missing_session_id(client: BackendGameClient, result: TestResult):
    """Test that missing session ID returns 400"""
    test_name = "Missing Session ID"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        print("\nTrying to process step without session ID...")

        try:
            response = client.process_step_raw({"input": "Test action"})
            if response.status_code == 400:
                print(f"  ✓ Correctly returned 400 for missing session ID")
            else:
                raise AssertionError(f"Expected 400 for missing session ID, got {response.status_code}")
        except AssertionError:
            raise
        except Exception as e:
            error_str = str(e)
            if "400" in error_str:
                print(f"  ✓ Correctly returned 400 for missing session ID")
            else:
                raise AssertionError(f"Expected 400 error, got: {error_str}")

        result.add(test_name, "success", time.time() - start_time)

    except AssertionError as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
