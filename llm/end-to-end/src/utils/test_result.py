"""Test result tracking"""

from typing import List, Dict, Any


class TestResult:
    """Tracks test results"""

    def __init__(self):
        """Initialize result tracker"""
        self.results: List[Dict[str, Any]] = []

    def add_result(self, name: str, status: str, message: str = "", details: Any = None):
        """Add a test result

        Args:
            name: Test name
            status: Test status (passed/failed)
            message: Status message
            details: Additional details
        """
        self.results.append({
            "name": name,
            "status": status,
            "message": message,
            "details": details
        })

    def print_summary(self):
        """Print summary of all test results"""
        print("\n" + "=" * 50)
        print("Test Results Summary")
        print("=" * 50)

        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        total = len(self.results)

        for result in self.results:
            status_symbol = "✓" if result["status"] == "passed" else "✗"
            print(f"{status_symbol} {result['name']}: {result['message']}")
            if result["details"]:
                print(f"  Details: {result['details']}")

        print("=" * 50)
        print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
        print("=" * 50)
        print()
