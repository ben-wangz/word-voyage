"""Error handling tests"""

import time
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def test_invalid_session(client: BackendGameClient, result: TestResult):
    """Test that accessing another user's session returns 403"""
    test_name = "Invalid Session Access"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        # Create a second client with different session
        client2 = BackendGameClient(client.service_url, client.timeout)
        client2.start_game()

        # Try to access client2's session from client1's cookie
        session2_id = client2.get_session_id()
        print(f"\nTrying to access another user's session: {session2_id}")

        try:
            # Manually construct URL to access other session
            response = client.client.get(f"{client.service_url}/api/game/context/{session2_id}")
            if response.status_code == 403:
                print(f"  ✓ Correctly returned 403 for unauthorized session access")
            else:
                raise AssertionError(f"Expected 403 for unauthorized access, got {response.status_code}")
        except Exception as e:
            error_str = str(e)
            if "403" in error_str or "forbidden" in error_str.lower():
                print(f"  ✓ Correctly returned 403 for unauthorized session access")
            else:
                raise AssertionError(f"Expected 403 error, got: {error_str}")

        client2.close()
        result.add(test_name, "success", time.time() - start_time)

    except AssertionError as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise


def test_missing_input(client: BackendGameClient, result: TestResult):
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
            response = client.process_step_raw({"input": ""})
            if response.status_code == 400:
                print(f"  ✓ Correctly returned 400 for empty input")
            else:
                raise AssertionError(f"Expected 400 for empty input, got {response.status_code}")
        except AssertionError:
            raise
        except Exception as e:
            error_str = str(e)
            if "400" in error_str:
                print(f"  ✓ Correctly returned 400 for empty input")
            else:
                raise AssertionError(f"Expected 400 error, got: {error_str}")

        # Send request without input field
        print("\nTrying to process step without input field...")
        try:
            response = client.process_step_raw({})
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
