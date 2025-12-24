"""Health check tests"""

import time
from ..utils.backend_client import BackendGameClient
from ..utils.test_result import TestResult


def test_health_check(client: BackendGameClient, result: TestResult):
    """Test /api/health endpoint"""
    test_name = "Health Check"
    start_time = time.time()

    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)

        health = client.health_check()

        print(f"\nHealth check response:")
        print(f"  Status: {health.get('status')}")
        print(f"  Service: {health.get('service')}")
        print(f"  Timestamp: {health.get('timestamp')}")

        # Validate response
        assert health.get('status') == 'ok', \
            f"Expected status=ok, got {health.get('status')}"

        assert health.get('service') == 'WordVoyage Backend API', \
            f"Expected service=WordVoyage Backend API, got {health.get('service')}"

        print("  ✓ Service is healthy")

        result.add(test_name, "success", time.time() - start_time)

    except Exception as e:
        result.add(test_name, "failed", time.time() - start_time, str(e))
        raise
