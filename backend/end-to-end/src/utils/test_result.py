"""Test result collector"""

from typing import List, Dict, Any


class TestResult:
    """Collect and display test results"""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def add(self, name: str, status: str, duration: float, error: str = None):
        """Add test result

        Args:
            name: Test name
            status: Test status (success/failed)
            duration: Test duration in seconds
            error: Error message if failed
        """
        self.results.append({
            "name": name,
            "status": status,
            "duration": duration,
            "error": error
        })

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "success")
        failed = sum(1 for r in self.results if r["status"] == "failed")

        for result in self.results:
            status_icon = "✓" if result["status"] == "success" else "✗"
            print(f"{status_icon} {result['name']}: {result['status']} ({result['duration']:.2f}s)")
            if result["error"]:
                print(f"  Error: {result['error']}")

        print("\n" + "-"*60)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        print("="*60)
